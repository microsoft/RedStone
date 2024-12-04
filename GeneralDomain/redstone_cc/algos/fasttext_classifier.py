import fasttext

fasttext.FastText.eprint = lambda x: None

FASTTEXT_LID_176_URL = (
    "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
)


class FastTextClassifier:
    def __init__(self, model_path):
        self.model = fasttext.load_model(model_path)

    def predict(self, text):
        if isinstance(text, list):
            text = " ".join(text)
        text = text.replace("\n", " ")

        labels, scores = self.model.predict(text, k=1)
        label, score = labels[0], scores[0]
        label = label.replace("__label__", "")

        return label, score
