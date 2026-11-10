class Strategy:
    """Base class for trading strategies."""
    def generate_signals(self, data):
        """Override this method to generate trading signals from data."""
        raise NotImplementedError
