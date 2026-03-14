import pygame
import random
import sys
import math
from hand_evaluator import HandEvaluator

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# Colors
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Card dimensions
CARD_WIDTH = 80
CARD_HEIGHT = 120

# Suits and ranks
SUITS = ['hearts', 'diamonds', 'clubs', 'spades']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# Suit symbols
SUIT_SYMBOLS = {
    'hearts': '♥',
    'diamonds': '♦',
    'clubs': '♣',
    'spades': '♠'
}

# Suit colors
SUIT_COLORS = {
    'hearts': RED,
    'diamonds': RED,
    'clubs': BLACK,
    'spades': BLACK
}

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.enabled = True
        # Try to initialize mixer
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self._generate_sounds()
        except Exception as e:
            print(f"Audio not available: {e}")
            self.enabled = False
    
    def _generate_sounds(self):
        """Generate simple beep sounds programmatically."""
        import array
        
        sample_rate = 22050
        
        # Sound definitions: (frequency, duration_ms, volume)
        sound_defs = {
            'bet': (600, 150, 0.3),      # Medium beep
            'raise': (700, 200, 0.4),    # Rising tone (simplified)
            'fold': (300, 300, 0.3),     # Low long beep
            'deal': (500, 80, 0.2),      # Quick click
            'win': (1000, 500, 0.4),     # High long beep (fanfare-like)
        }
        
        for name, (freq, duration_ms, volume) in sound_defs.items():
            try:
                # Calculate number of samples
                num_samples = int(sample_rate * duration_ms / 1000)
                
                # Generate sine wave samples
                buf = array.array('h', [0] * num_samples)
                amplitude = int(32767 * volume)
                
                for i in range(num_samples):
                    t = i / sample_rate
                    # Simple sine wave
                    value = int(amplitude * math.sin(2 * math.pi * freq * t))
                    # Apply fade out to avoid clicking
                    fade = 1.0 - (i / num_samples) * 0.5
                    buf[i] = int(value * fade)
                
                # Create sound from buffer
                sound = pygame.mixer.Sound(buffer=buf)
                self.sounds[name] = sound
            except Exception as e:
                print(f"Could not generate sound '{name}': {e}")
                self.sounds[name] = None
        
        # Generate special "check" sound - wood knock
        try:
            self.sounds['check'] = self._generate_wood_knock()
        except Exception as e:
            print(f"Could not generate wood knock sound: {e}")
            self.sounds['check'] = None
    
    def _generate_wood_knock(self):
        """Generate a wood knock sound."""
        import array
        
        sample_rate = 22050
        duration_ms = 150  # Short knock
        num_samples = int(sample_rate * duration_ms / 1000)
        buf = array.array('h', [0] * num_samples)
        
        # Wood knock characteristics:
        # 1. Quick attack (sharp onset)
        # 2. Mix of low frequency thud + noise burst
        # 3. Quick exponential decay
        # 4. Some resonance
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Envelope: very quick attack, exponential decay
            attack_samples = int(0.003 * sample_rate)  # 3ms attack
            if i < attack_samples:
                envelope = i / attack_samples
            else:
                # Exponential decay
                decay_rate = 30  # Faster decay for knock
                envelope = math.exp(-decay_rate * (t - 0.003))
            
            # Low frequency "thud" component (around 100-200 Hz)
            thud_freq = 150
            thud = math.sin(2 * math.pi * thud_freq * t)
            
            # Add some higher harmonics for "wood" character
            harmonic1 = 0.3 * math.sin(2 * math.pi * thud_freq * 2 * t)
            harmonic2 = 0.15 * math.sin(2 * math.pi * thud_freq * 3 * t)
            
            # Add noise burst for the "impact"
            noise = random.uniform(-1, 1) * 0.4
            
            # Combine components
            sample = thud + harmonic1 + harmonic2 + noise
            sample *= envelope * 0.5  # Volume control
            
            # Add a second "echo" knock slightly delayed and quieter
            echo_delay = 0.02  # 20ms delay
            echo_time = t - echo_delay
            if echo_time > 0:
                echo_envelope = math.exp(-25 * echo_time) * 0.3
                echo_thud = math.sin(2 * math.pi * thud_freq * echo_time)
                echo_noise = random.uniform(-1, 1) * 0.2
                sample += (echo_thud + echo_noise) * echo_envelope
            
            # Clamp and convert to 16-bit
            value = int(sample * 32767)
            value = max(-32767, min(32767, value))
            buf[i] = value
        
        return pygame.mixer.Sound(buffer=buf)

    def play(self, name):
        if not self.enabled:
            return
        if self.sounds.get(name):
            try:
                self.sounds[name].play()
            except Exception as e:
                print(f"Error playing sound '{name}': {e}")

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 255
        self.gravity = 0.1

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 5
        
    def draw(self, surface):
        if self.life > 0:
            alpha_color = list(self.color) + [self.life]
            # Pygame draw.circle doesn't support alpha directly on main surface
            # So we just draw solid or fade out by not drawing
            if self.life > 10:
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        colors = [RED, GOLD, BLUE, WHITE, (0, 255, 0), (255, 0, 255)]
        color = random.choice(colors)
        for _ in range(50):
            self.particles.append(Particle(x, y, color))
            
    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        return len(self.particles) > 0
        
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

class Card:
    """Represents a playing card with animation capabilities."""
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.face_up = False
        # Start position (center of screen / deck)
        self.x = SCREEN_WIDTH // 2 - CARD_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
        self.target_x = self.x
        self.target_y = self.y
        self.speed = 25
        self.arrived = True
    
    def __str__(self):
        return f"{self.rank} of {self.suit}"
    
    def __repr__(self):
        return f"Card('{self.suit}', '{self.rank}')"
    
    def move_to(self, x, y):
        self.target_x = x
        self.target_y = y
        self.arrived = False
        
    def update(self):
        if self.arrived:
            return

        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist < self.speed:
            self.x = self.target_x
            self.y = self.target_y
            self.arrived = True
        else:
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * self.speed
            self.y += math.sin(angle) * self.speed
    
    def render(self, surface):
        """Render the card at its current position."""
        card_rect = pygame.Rect(int(self.x), int(self.y), CARD_WIDTH, CARD_HEIGHT)
        
        if self.face_up:
            pygame.draw.rect(surface, WHITE, card_rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, card_rect, 2, border_radius=8)
            
            color = SUIT_COLORS[self.suit]
            symbol = SUIT_SYMBOLS[self.suit]
            
            rank_font = pygame.font.SysFont('Arial', 20, bold=True)
            suit_font = pygame.font.SysFont('Arial', 24)
            center_font = pygame.font.SysFont('Arial', 36)
            
            rank_text = rank_font.render(self.rank, True, color)
            suit_text = suit_font.render(symbol, True, color)
            surface.blit(rank_text, (self.x + 5, self.y + 5))
            surface.blit(suit_text, (self.x + 5, self.y + 22))
            
            center_text = center_font.render(symbol, True, color)
            center_rect = center_text.get_rect(center=(self.x + CARD_WIDTH // 2, self.y + CARD_HEIGHT // 2))
            surface.blit(center_text, center_rect)
            
            rank_text_br = rank_font.render(self.rank, True, color)
            suit_text_br = suit_font.render(symbol, True, color)
            surface.blit(rank_text_br, (self.x + CARD_WIDTH - 22, self.y + CARD_HEIGHT - 25))
            surface.blit(suit_text_br, (self.x + CARD_WIDTH - 22, self.y + CARD_HEIGHT - 42))
        else:
            pygame.draw.rect(surface, BLUE, card_rect, border_radius=8)
            pygame.draw.rect(surface, BLACK, card_rect, 2, border_radius=8)
            inner_rect = pygame.Rect(self.x + 5, self.y + 5, CARD_WIDTH - 10, CARD_HEIGHT - 10)
            pygame.draw.rect(surface, (25, 25, 112), inner_rect, border_radius=5)
            pattern_font = pygame.font.SysFont('Arial', 28)
            for i in range(3):
                for j in range(4):
                    pattern_text = pattern_font.render('♦', True, GOLD)
                    surface.blit(pattern_text, (self.x + 10 + i * 25, self.y + 10 + j * 28))

class Deck:
    """Represents a deck of 52 playing cards."""
    def __init__(self):
        self.cards = []
        self.reset()
    
    def reset(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self, num_cards=1):
        dealt_cards = []
        for _ in range(num_cards):
            if self.cards:
                dealt_cards.append(self.cards.pop())
        return dealt_cards
    
    def cards_remaining(self):
        return len(self.cards)

class Button:
    """Represents a clickable button."""
    def __init__(self, x, y, width, height, text, color=BLUE, hover_color=None, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color or tuple(min(c + 30, 255) for c in color)
        self.action = action
        self.is_hovered = False
        self.visible = True
        self.enabled = True
    
    def draw(self, surface):
        if not self.visible:
            return
        
        color = self.hover_color if self.is_hovered and self.enabled else self.color
        if not self.enabled:
            color = GRAY
            
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        font = pygame.font.SysFont('Arial', 20, bold=True)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if not self.visible or not self.enabled:
            return False
        
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False

class Slider:
    """Slider for selecting bet amount."""
    def __init__(self, x, y, width, min_val, max_val):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = min_val
        self.dragging = False
        self.handle_rect = pygame.Rect(x, y - 5, 10, 30)
        self.visible = False
        
    def draw(self, surface):
        if not self.visible:
            return
            
        pygame.draw.rect(surface, GRAY, self.rect)
        pygame.draw.rect(surface, WHITE, self.handle_rect)
        
        # Draw value text
        font = pygame.font.SysFont('Arial', 16)
        text = font.render(str(int(self.value)), True, WHITE)
        surface.blit(text, (self.rect.x + self.rect.width + 10, self.rect.y))

    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.handle_rect.x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
                ratio = (self.handle_rect.x - self.rect.x) / self.rect.width
                self.value = self.min_val + ratio * (self.max_val - self.min_val)
                return True
        return False

class Player:
    """Represents a poker player."""
    def __init__(self, name, position, bananas=100, is_ai=False, ai_type=None):
        self.name = name
        self.position = position # 'bottom', 'left', 'right'
        self.bananas = bananas
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.active = True
        self.action_text = ""
        self.is_ai = is_ai
        self.ai_type = ai_type  # 'rock', 'calling_station', or None
        
        # Calculate hand position for this player
        if self.position == 'bottom':
            self.hand_x = SCREEN_WIDTH // 2 - CARD_WIDTH - 5
            self.hand_y = SCREEN_HEIGHT - 150
        elif self.position == 'left':
            self.hand_x = 50
            self.hand_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
        elif self.position == 'right':
            self.hand_x = SCREEN_WIDTH - 250
            self.hand_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
            
    def reset_round(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.active = True
        self.action_text = ""


class AIPlayer:
    """AI decision-making for poker players."""
    
    # Rank values for pre-flop evaluation
    RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    
    @staticmethod
    def evaluate_preflop_hand(cards):
        """
        Evaluate the strength of a 2-card starting hand.
        Returns a score from 0-100.
        """
        if len(cards) != 2:
            return 0
        
        ranks = [AIPlayer.RANK_VALUES[c.rank] for c in cards]
        suits = [c.suit for c in cards]
        
        high = max(ranks)
        low = min(ranks)
        is_pair = ranks[0] == ranks[1]
        is_suited = suits[0] == suits[1]
        gap = high - low
        
        score = 0
        
        # Pairs are strong
        if is_pair:
            score = 50 + high * 3  # 22=56, AA=92
        else:
            # High cards
            score = high + low
            
            # Suited bonus
            if is_suited:
                score += 8
            
            # Connected cards bonus (smaller gap = better)
            if gap <= 2:
                score += 5 - gap
            
            # Ace-X hands are strong
            if high == 14:
                score += 10
        
        return min(100, score)
    
    @staticmethod
    def evaluate_hand_strength(player, community_cards):
        """
        Evaluate the current hand strength considering community cards.
        Returns a score from 0-100.
        """
        if not player.hand:
            return 0
        
        if not community_cards:
            return AIPlayer.evaluate_preflop_hand(player.hand)
        
        # Use HandEvaluator for post-flop
        full_hand = player.hand + community_cards
        score = HandEvaluator.evaluate(full_hand)
        
        # Convert hand category to strength score
        category = score[0]
        
        # Map categories to base scores
        category_scores = {
            0: 10,   # High Card
            1: 25,   # Pair
            2: 35,   # Two Pair
            3: 50,   # Three of a Kind
            4: 60,   # Straight
            5: 65,   # Flush
            6: 75,   # Full House
            7: 85,   # Four of a Kind
            8: 95,   # Straight Flush
            9: 100   # Royal Flush
        }
        
        base_score = category_scores.get(category, 10)
        
        # Add tie-breaker influence (small adjustment)
        tie_breakers = score[1]
        if tie_breakers:
            # Add a small bonus based on high cards
            bonus = sum(tie_breakers[:2]) / 30  # Small adjustment
            base_score = min(100, base_score + bonus)
        
        return base_score
    
    @staticmethod
    def decide_rock(player, community_cards, current_bet, pot):
        """
        'The Rock' - Tight-passive player.
        Only plays strong hands, folds easily.
        Rarely raises, mostly calls or folds.
        """
        strength = AIPlayer.evaluate_hand_strength(player, community_cards)
        call_amount = current_bet - player.current_bet
        
        # Pre-flop: Only play premium hands (pairs 8+, AK, AQ, AJ suited)
        if not community_cards:
            if strength < 60:  # Weak hand
                if call_amount > 0:
                    return ('fold', 0)
                else:
                    return ('check', 0)
            elif strength >= 75:  # Strong hand
                if random.random() < 0.3:  # Sometimes raise with very strong hands
                    raise_amount = min(20, player.bananas)
                    return ('raise', raise_amount)
        
        # Post-flop
        else:
            if strength < 40:
                if call_amount > 0:
                    return ('fold', 0)
                else:
                    return ('check', 0)
            elif strength >= 70 and random.random() < 0.2:
                raise_amount = min(15, player.bananas)
                return ('raise', raise_amount)
        
        # Default: call if reasonable, otherwise check
        if call_amount > 0:
            if call_amount <= player.bananas and strength >= 50:
                return ('call', call_amount)
            else:
                return ('fold', 0)
        else:
            return ('check', 0)
    
    @staticmethod
    def decide_calling_station(player, community_cards, current_bet, pot):
        """
        'Calling Station' - Loose-passive player.
        Almost always calls, rarely raises.
        Plays almost any hand.
        """
        strength = AIPlayer.evaluate_hand_strength(player, community_cards)
        call_amount = current_bet - player.current_bet
        
        # Very rarely folds
        if call_amount > 0:
            # Only fold with extremely weak hands and high bets
            if strength < 20 and call_amount > 30:
                return ('fold', 0)
            
            # Almost always call
            if call_amount <= player.bananas:
                return ('call', call_amount)
            else:
                return ('fold', 0)
        
        # Can check
        if current_bet == player.current_bet:
            # Rarely raise, even with strong hands
            if strength >= 80 and random.random() < 0.1:
                raise_amount = min(10, player.bananas)
                return ('raise', raise_amount)
            return ('check', 0)
        
        # Default: call
        if call_amount <= player.bananas:
            return ('call', call_amount)
        return ('fold', 0)
    
    @staticmethod
    def make_decision(player, community_cards, current_bet, pot):
        """
        Make a decision based on the player's AI type.
        Returns (action, amount) tuple.
        """
        if player.ai_type == 'rock':
            return AIPlayer.decide_rock(player, community_cards, current_bet, pot)
        elif player.ai_type == 'calling_station':
            return AIPlayer.decide_calling_station(player, community_cards, current_bet, pot)
        else:
            # Default: random action
            actions = ['check', 'call', 'fold']
            return (random.choice(actions), 0)

class PokerGame:
    """Main poker game class."""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Poker Game")
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        
        self.deck = Deck()
        # Player at bottom is human, left is "Rock", right is "Calling Station"
        self.players = [
            Player("You", "bottom", is_ai=False),
            Player("Rock", "left", is_ai=True, ai_type='rock'),
            Player("Station", "right", is_ai=True, ai_type='calling_station')
        ]
        self.current_player_idx = 0
        self.dealer_idx = 0
        
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.game_phase = "pre-start" # pre-start, pre-flop, flop, turn, river, showdown
        
        # Animation state
        self.animating = False
        self.deal_queue = [] # List of (card, target_x, target_y, face_up, delay)
        self.fireworks = []
        self.animation_timer = 0
        
        # AI turn handling
        self.ai_turn_pending = False
        self.ai_turn_timer = 0
        self.ai_delay = 1000  # 1 second delay for AI actions
        
        # UI Elements
        self.start_button = Button(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT // 2 - 25, 150, 50, "START", GOLD, action=self.start_game)
        self.deal_button = Button(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 150, 150, 50, "DEAL", GREEN, action=self.start_dealing_sequence)
        self.deal_button.visible = False
        
        # Betting Controls
        self.check_button = Button(SCREEN_WIDTH - 350, SCREEN_HEIGHT - 100, 100, 40, "CHECK", BLUE, action=self.check)
        self.call_button = Button(SCREEN_WIDTH - 240, SCREEN_HEIGHT - 100, 100, 40, "CALL", BLUE, action=self.call)
        self.raise_button = Button(SCREEN_WIDTH - 130, SCREEN_HEIGHT - 100, 100, 40, "RAISE", BLUE, action=self.raise_bet)
        self.fold_button = Button(SCREEN_WIDTH - 460, SCREEN_HEIGHT - 100, 100, 40, "FOLD", RED, action=self.fold)
        
        self.raise_slider = Slider(SCREEN_WIDTH - 350, SCREEN_HEIGHT - 50, 200, 0, 100)
        
        self.betting_buttons = [self.check_button, self.call_button, self.raise_button, self.fold_button]
        for btn in self.betting_buttons:
            btn.visible = False
            
        self.running = True
        self.message = ""

    def start_game(self):
        self.game_phase = "start"
        self.start_button.visible = False
        self.deal_button.visible = True
        self.deck.shuffle()
        self.message = "Press DEAL to start"

    def start_dealing_sequence(self):
        self.deck.reset()
        self.deck.shuffle()
        self.sound_manager.play('deal')
        
        for player in self.players:
            player.reset_round()
            
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.deal_button.visible = False
        self.game_phase = "dealing"
        
        # Queue up dealing animations
        self.deal_queue = []
        
        # Deal 2 cards to each player, one by one
        for i in range(2):
            for player in self.players:
                card = self.deck.deal(1)[0]
                player.hand.append(card)
                
                # Calculate target position
                target_x = player.hand_x + i * (CARD_WIDTH + 5)
                target_y = player.hand_y
                
                self.deal_queue.append({
                    'card': card,
                    'target_x': target_x,
                    'target_y': target_y,
                    'face_up': True, # Face up for all players as per previous logic
                    'delay': 200 * (len(self.deal_queue) + 1) # Stagger animations
                })
        
        self.animating = True
        self.animation_timer = pygame.time.get_ticks()

    def update_animations(self):
        current_time = pygame.time.get_ticks()
        
        # Process deal queue
        if self.deal_queue:
            # Check if it's time for the next card
            if current_time - self.animation_timer > 200: # 200ms delay between cards
                next_deal = self.deal_queue.pop(0)
                card = next_deal['card']
                card.move_to(next_deal['target_x'], next_deal['target_y'])
                card.face_up = next_deal['face_up']
                self.sound_manager.play('deal')
                self.animation_timer = current_time
        elif self.animating and self.game_phase == "dealing":
            # Check if all cards have arrived
            all_arrived = True
            for player in self.players:
                for card in player.hand:
                    if not card.arrived:
                        all_arrived = False
                        break
            
            if all_arrived:
                self.animating = False
                self.game_phase = "pre-flop"
                self.current_player_idx = (self.dealer_idx + 1) % len(self.players)
                self.update_betting_ui()
                self.message = f"{self.players[self.current_player_idx].name}'s turn"
                # Start AI turn if needed
                self.check_ai_turn()

        # Handle AI turns with delay
        if self.ai_turn_pending:
            if current_time - self.ai_turn_timer >= self.ai_delay:
                self.ai_turn_pending = False
                self.execute_ai_action()

        # Update all cards
        for player in self.players:
            for card in player.hand:
                card.update()
        for card in self.community_cards:
            card.update()
            
        # Update fireworks
        for fw in self.fireworks:
            if not fw.update():
                self.fireworks.remove(fw)
    
    def check_ai_turn(self):
        """Check if current player is AI and start their turn."""
        if self.game_phase in ["pre-flop", "flop", "turn", "river"]:
            current_player = self.players[self.current_player_idx]
            if current_player.is_ai and not current_player.folded:
                self.ai_turn_pending = True
                self.ai_turn_timer = pygame.time.get_ticks()
                self.message = f"{current_player.name} is thinking..."
    
    def execute_ai_action(self):
        """Execute the AI's decision."""
        player = self.players[self.current_player_idx]
        if not player.is_ai or player.folded:
            return
        
        # Get AI decision
        action, amount = AIPlayer.make_decision(
            player, 
            self.community_cards, 
            self.current_bet, 
            self.pot
        )
        
        # Execute the action
        if action == 'check':
            self.check()
        elif action == 'call':
            self.call()
        elif action == 'raise':
            self.raise_slider.value = amount
            self.raise_bet()
        elif action == 'fold':
            self.fold()
        else:
            # Default to check if can, otherwise fold
            if self.current_bet == player.current_bet:
                self.check()
            else:
                self.fold()

    def next_phase(self):
        # Reset bets for new phase
        for p in self.players:
            p.current_bet = 0
        self.current_bet = 0
        self.current_player_idx = (self.dealer_idx + 1) % len(self.players)
        
        new_cards = []
        if self.game_phase == "pre-flop":
            self.game_phase = "flop"
            new_cards = self.deck.deal(3)
        elif self.game_phase == "flop":
            self.game_phase = "turn"
            new_cards = self.deck.deal(1)
        elif self.game_phase == "turn":
            self.game_phase = "river"
            new_cards = self.deck.deal(1)
        elif self.game_phase == "river":
            self.game_phase = "showdown"
            self.determine_winner()
            return

        # Animate community cards
        slot_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
        start_x = SCREEN_WIDTH // 2 - (5 * (CARD_WIDTH + 10)) // 2
        current_count = len(self.community_cards)
        
        for i, card in enumerate(new_cards):
            self.community_cards.append(card)
            target_x = start_x + (current_count + i) * (CARD_WIDTH + 10)
            card.move_to(target_x, slot_y)
            card.face_up = True
            self.sound_manager.play('deal')

        self.update_betting_ui()
        self.message = f"Phase: {self.game_phase}. {self.players[self.current_player_idx].name}'s turn"
        # Check if AI should take turn
        self.check_ai_turn()

    def check(self):
        self.sound_manager.play('check')
        player = self.players[self.current_player_idx]
        player.action_text = "Check"
        self.next_turn()

    def call(self):
        self.sound_manager.play('bet')
        player = self.players[self.current_player_idx]
        amount = self.current_bet - player.current_bet
        if player.bananas >= amount:
            player.bananas -= amount
            player.current_bet += amount
            self.pot += amount
            player.action_text = "Call"
            self.next_turn()

    def raise_bet(self):
        self.sound_manager.play('raise')
        player = self.players[self.current_player_idx]
        amount = int(self.raise_slider.value)
        total_bet = self.current_bet + amount
        cost = total_bet - player.current_bet
        
        if player.bananas >= cost:
            player.bananas -= cost
            player.current_bet += cost
            self.pot += cost
            self.current_bet = total_bet
            player.action_text = f"Raise {amount}"
            self.next_turn()

    def fold(self):
        self.sound_manager.play('fold')
        player = self.players[self.current_player_idx]
        player.folded = True
        player.action_text = "Fold"
        
        # Animate cards flying away
        for card in player.hand:
            # Fly off screen in random direction
            angle = random.uniform(0, 2 * math.pi)
            dist = 1000
            target_x = card.x + math.cos(angle) * dist
            target_y = card.y + math.sin(angle) * dist
            card.move_to(target_x, target_y)
            
        self.next_turn()

    def next_turn(self):
        # Find next active player
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            self.game_phase = "showdown"
            self.determine_winner()
            return

        # Check if round is complete
        all_matched = True
        for p in active_players:
            if p.current_bet != self.current_bet:
                all_matched = False
                break
        
        if all_matched and self.current_player_idx == self.dealer_idx:
             self.next_phase()
        else:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            while self.players[self.current_player_idx].folded:
                self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            
            self.update_betting_ui()
            self.message = f"{self.players[self.current_player_idx].name}'s turn"
            # Check if AI should take turn
            self.check_ai_turn()

    def update_betting_ui(self):
        player = self.players[self.current_player_idx]
        # Only show UI for human players
        show_ui = (self.game_phase in ["pre-flop", "flop", "turn", "river"] 
                   and not self.animating 
                   and not player.is_ai)
        
        for btn in self.betting_buttons:
            btn.visible = show_ui
        self.raise_slider.visible = show_ui
        
        if show_ui:
            self.raise_slider.max_val = player.bananas
            if self.current_bet > player.current_bet:
                self.check_button.enabled = False
                self.call_button.enabled = True
                self.call_button.text = f"CALL {self.current_bet - player.current_bet}"
            else:
                self.check_button.enabled = True
                self.call_button.enabled = False
                self.call_button.text = "CALL"

    def determine_winner(self):
        self.sound_manager.play('win')
        active_players = [p for p in self.players if not p.folded]
        
        if not active_players:
            return

        best_hand_val = -1
        winners = []
        winner_hand_name = ""
        
        if len(active_players) == 1:
            winners = active_players
            winner_hand_name = "Last Man Standing"
        else:
            for player in active_players:
                full_hand = player.hand + self.community_cards
                score = HandEvaluator.evaluate(full_hand)
                player_score_val = (score[0], score[1])
                
                if not winners:
                    winners = [player]
                    best_hand_val = player_score_val
                    winner_hand_name = score[2]
                else:
                    if player_score_val > best_hand_val:
                        winners = [player]
                        best_hand_val = player_score_val
                        winner_hand_name = score[2]
                    elif player_score_val == best_hand_val:
                        winners.append(player)

        # Distribute pot
        split_amount = self.pot // len(winners)
        winner_names = []
        for winner in winners:
            winner.bananas += split_amount
            winner_names.append(winner.name)
            
            # Launch fireworks for winner
            if winner.position == 'bottom':
                fx, fy = SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100
            elif winner.position == 'left':
                fx, fy = 100, SCREEN_HEIGHT // 2
            elif winner.position == 'right':
                fx, fy = SCREEN_WIDTH - 100, SCREEN_HEIGHT // 2
            
            for _ in range(5):
                self.fireworks.append(Firework(fx + random.randint(-50, 50), fy + random.randint(-50, 50)))
            
        self.message = f"Winner: {', '.join(winner_names)} ({winner_hand_name}). Pot: {self.pot}"
        self.deal_button.visible = True
        
        # Hide betting UI
        for btn in self.betting_buttons:
            btn.visible = False
        self.raise_slider.visible = False

    def draw(self):
        self.screen.fill(DARK_GREEN)
        
        # Draw table
        table_rect = pygame.Rect(100, 100, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200)
        pygame.draw.ellipse(self.screen, GREEN, table_rect)
        pygame.draw.ellipse(self.screen, (139, 69, 19), table_rect, 8)
        
        # Draw community card slots
        slot_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2
        start_x = SCREEN_WIDTH // 2 - (5 * (CARD_WIDTH + 10)) // 2
        for i in range(5):
            x = start_x + i * (CARD_WIDTH + 10)
            slot_rect = pygame.Rect(x, slot_y, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(self.screen, (0, 100, 0), slot_rect, 2, border_radius=8)
            
        # Draw community cards
        for i, card in enumerate(self.community_cards):
            card.render(self.screen)

        # Draw Players
        for player in self.players:
            # Draw cards
            for i, card in enumerate(player.hand):
                card.render(self.screen)
            
            # Draw Info
            font = pygame.font.SysFont('Arial', 18, bold=True)
            info_text = f"{player.name}: {player.bananas} 🍌"
            if player.current_bet > 0:
                info_text += f" (Bet: {player.current_bet})"
            if player.folded:
                info_text += " [FOLDED]"
            
            # Position info text relative to player position
            if player.position == 'bottom':
                tx, ty = SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 180
            elif player.position == 'left':
                tx, ty = 50, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2 - 30
            elif player.position == 'right':
                tx, ty = SCREEN_WIDTH - 250, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2 - 30
                
            text_surf = font.render(info_text, True, WHITE)
            self.screen.blit(text_surf, (tx, ty))
            
            if player.action_text:
                action_surf = font.render(player.action_text, True, GOLD)
                self.screen.blit(action_surf, (tx, ty - 20))

        # Draw Pot
        pot_font = pygame.font.SysFont('Arial', 24, bold=True)
        pot_text = pot_font.render(f"Pot: {self.pot}", True, GOLD)
        pot_rect = pot_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(pot_text, pot_rect)

        # Draw UI
        self.start_button.draw(self.screen)
        self.deal_button.draw(self.screen)
        for btn in self.betting_buttons:
            btn.draw(self.screen)
        self.raise_slider.draw(self.screen)
        
        # Draw Message
        msg_font = pygame.font.SysFont('Arial', 24)
        msg_text = msg_font.render(self.message, True, WHITE)
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(msg_text, msg_rect)
        
        # Draw Fireworks
        for fw in self.fireworks:
            fw.draw(self.screen)

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if not self.animating:
                self.start_button.handle_event(event)
                self.deal_button.handle_event(event)
                for btn in self.betting_buttons:
                    btn.handle_event(event)
                self.raise_slider.handle_event(event)

    def run(self):
        while self.running:
            self.handle_events()
            self.update_animations()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PokerGame()
    game.run()
