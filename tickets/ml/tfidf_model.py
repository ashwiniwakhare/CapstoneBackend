from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Prototype text representing a highly urgent ticket
URGENT_PROTOTYPE = (
    "urgent payment failed critical error crash "
    "data loss down not working immediate"
)

class TFIDFUrgency:
    """
    TF-IDF based urgency scoring model.
    Compares ticket text with an 'urgent prototype'
    using cosine similarity.
    """

    def __init__(self):
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000
        )
        self.fitted = False

    def fit_on_texts(self, texts):
        """
        Fit TF-IDF on ticket texts.
        If no tickets exist, fit only on urgent prototype.
        """
        if not texts:
            self.vectorizer.fit([URGENT_PROTOTYPE])
            self.fitted = True
            return

        # Fit on all ticket texts + urgent reference text
        self.vectorizer.fit(texts + [URGENT_PROTOTYPE])
        self.fitted = True

    def score_texts(self, texts):
        """
        Calculate urgency score for each ticket
        based on cosine similarity with urgent prototype.
        """
        if not self.fitted:
            self.fit_on_texts(texts)

        # Create corpus with tickets + prototype
        corpus = texts + [URGENT_PROTOTYPE]

        # Transform text to TF-IDF vectors
        X = self.vectorizer.transform(corpus)

        # Separate ticket vectors and urgent prototype vector
        ticket_vecs = X[:-1]
        proto_vec = X[-1]

        # Compute cosine similarity scores
        sims = cosine_similarity(
            ticket_vecs,
            proto_vec.reshape(1, -1)
        ).ravel()

        return sims


# Singleton model instance (shared across calls)
_model = TFIDFUrgency()


def fit_model_on_tickets(texts):
    """
    Fit TF-IDF model on historical ticket descriptions.
    """
    _model.fit_on_texts(texts)


def predict_scores_for_tickets(texts):
    """
    Predict urgency scores for new tickets.
    Higher score = more urgent ticket.
    """
    return _model.score_texts(texts)
