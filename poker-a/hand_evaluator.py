from collections import Counter

class HandEvaluator:
    """Evaluates 7-card poker hands and determines the best 5-card combination."""
    
    # Rank values for comparison
    RANK_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    
    # Hand categories
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9
    
    CATEGORY_NAMES = {
        HIGH_CARD: "High Card",
        PAIR: "Pair",
        TWO_PAIR: "Two Pair",
        THREE_OF_A_KIND: "Three of a Kind",
        STRAIGHT: "Straight",
        FLUSH: "Flush",
        FULL_HOUSE: "Full House",
        FOUR_OF_A_KIND: "Four of a Kind",
        STRAIGHT_FLUSH: "Straight Flush",
        ROYAL_FLUSH: "Royal Flush"
    }
    
    @staticmethod
    def evaluate(cards):
        """
        Evaluate the best 5-card hand from a list of 7 cards.
        Returns a tuple: (category_score, tie_breaker_list, hand_name)
        """
        if len(cards) < 5:
            return (0, [], "Incomplete Hand")
            
        # Convert cards to easier format for processing
        # Each card is (rank_value, suit)
        processed_cards = []
        for card in cards:
            processed_cards.append((HandEvaluator.RANK_VALUES[card.rank], card.suit))
            
        processed_cards.sort(key=lambda x: x[0], reverse=True)
        
        # Check for each hand type from highest to lowest
        
        # Check for Straight Flush and Royal Flush
        straight_flush = HandEvaluator._check_straight_flush(processed_cards)
        if straight_flush:
            if straight_flush[1][0] == 14: # Ace high straight flush
                return (HandEvaluator.ROYAL_FLUSH, [], "Royal Flush")
            return (HandEvaluator.STRAIGHT_FLUSH, straight_flush[1], "Straight Flush")
            
        # Check for Four of a Kind
        four_kind = HandEvaluator._check_four_of_a_kind(processed_cards)
        if four_kind:
            return (HandEvaluator.FOUR_OF_A_KIND, four_kind, "Four of a Kind")
            
        # Check for Full House
        full_house = HandEvaluator._check_full_house(processed_cards)
        if full_house:
            return (HandEvaluator.FULL_HOUSE, full_house, "Full House")
            
        # Check for Flush
        flush = HandEvaluator._check_flush(processed_cards)
        if flush:
            return (HandEvaluator.FLUSH, flush, "Flush")
            
        # Check for Straight
        straight = HandEvaluator._check_straight(processed_cards)
        if straight:
            return (HandEvaluator.STRAIGHT, straight, "Straight")
            
        # Check for Three of a Kind
        three_kind = HandEvaluator._check_three_of_a_kind(processed_cards)
        if three_kind:
            return (HandEvaluator.THREE_OF_A_KIND, three_kind, "Three of a Kind")
            
        # Check for Two Pair
        two_pair = HandEvaluator._check_two_pair(processed_cards)
        if two_pair:
            return (HandEvaluator.TWO_PAIR, two_pair, "Two Pair")
            
        # Check for Pair
        pair = HandEvaluator._check_pair(processed_cards)
        if pair:
            return (HandEvaluator.PAIR, pair, "Pair")
            
        # High Card
        high_card_ranks = [c[0] for c in processed_cards[:5]]
        return (HandEvaluator.HIGH_CARD, high_card_ranks, "High Card")

    @staticmethod
    def _check_straight_flush(cards):
        # Group by suit
        suits = {}
        for rank, suit in cards:
            if suit not in suits:
                suits[suit] = []
            suits[suit].append(rank)
            
        for suit in suits:
            if len(suits[suit]) >= 5:
                # Check for straight within this suit
                suit_cards = sorted(list(set(suits[suit])), reverse=True)
                straight = HandEvaluator._find_straight_in_ranks(suit_cards)
                if straight:
                    return True, straight
        return False

    @staticmethod
    def _check_four_of_a_kind(cards):
        ranks = [c[0] for c in cards]
        counts = Counter(ranks)
        for rank, count in counts.items():
            if count == 4:
                # Get kicker
                kickers = [r for r in ranks if r != rank]
                return [rank] + kickers[:1]
        return False

    @staticmethod
    def _check_full_house(cards):
        ranks = [c[0] for c in cards]
        counts = Counter(ranks)
        three_kind = []
        two_kind = []
        
        for rank, count in counts.items():
            if count >= 3:
                three_kind.append(rank)
            elif count >= 2:
                two_kind.append(rank)
                
        three_kind.sort(reverse=True)
        two_kind.sort(reverse=True)
        
        if len(three_kind) >= 1:
            best_three = three_kind[0]
            # Look for pair (could be another set of 3 treated as pair)
            remaining = [r for r in three_kind if r != best_three] + two_kind
            remaining.sort(reverse=True)
            
            if len(remaining) >= 1:
                return [best_three, remaining[0]]
                
        return False

    @staticmethod
    def _check_flush(cards):
        suits = [c[1] for c in cards]
        suit_counts = Counter(suits)
        for suit, count in suit_counts.items():
            if count >= 5:
                flush_cards = [c[0] for c in cards if c[1] == suit]
                flush_cards.sort(reverse=True)
                return flush_cards[:5]
        return False

    @staticmethod
    def _check_straight(cards):
        ranks = sorted(list(set([c[0] for c in cards])), reverse=True)
        straight = HandEvaluator._find_straight_in_ranks(ranks)
        return straight

    @staticmethod
    def _find_straight_in_ranks(ranks):
        # Handle Ace low straight (A, 5, 4, 3, 2)
        if 14 in ranks:
            ranks_with_low_ace = ranks + [1]
        else:
            ranks_with_low_ace = ranks
            
        for i in range(len(ranks_with_low_ace) - 4):
            window = ranks_with_low_ace[i:i+5]
            if window[0] - window[4] == 4:
                return window
        return False

    @staticmethod
    def _check_three_of_a_kind(cards):
        ranks = [c[0] for c in cards]
        counts = Counter(ranks)
        for rank, count in counts.items():
            if count == 3:
                kickers = [r for r in ranks if r != rank]
                return [rank] + kickers[:2]
        return False

    @staticmethod
    def _check_two_pair(cards):
        ranks = [c[0] for c in cards]
        counts = Counter(ranks)
        pairs = [r for r, c in counts.items() if c >= 2]
        pairs.sort(reverse=True)
        
        if len(pairs) >= 2:
            kickers = [r for r in ranks if r != pairs[0] and r != pairs[1]]
            return pairs[:2] + kickers[:1]
        return False

    @staticmethod
    def _check_pair(cards):
        ranks = [c[0] for c in cards]
        counts = Counter(ranks)
        for rank, count in counts.items():
            if count == 2:
                kickers = [r for r in ranks if r != rank]
                return [rank] + kickers[:3]
        return False
