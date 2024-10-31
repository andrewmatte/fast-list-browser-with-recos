from llama_cpp import Llama
import serde_bin_vec
import numpy as np
from sklearn.decomposition import PCA


def right_pad(word):
    while len(word) < 40:
        word += ' '
    return word

# this is the reference to an LLM. whatever you choose is probably fine
gguf_path = "/home/andrew/Downloads/bge-large-en-v1.5-f32.gguf"
model = Llama(gguf_path, embedding=True)
upper_chars = set("QWERTYUIOPASDFGHJKLZXCVBNM")
file = open("/usr/share/dict/american-english", "r").read().split("\n")[:-1]
words = [w for w in file if w[0] not in upper_chars and "'" not in w]
chars = set(''.join(upper_chars).lower())

# I get rid of non base-case words here and am padding to create IDs in the vector database
to_remove = []
for word in words:
    for char in word:
        if char not in chars:
            to_remove.append(word)


for word in to_remove:
    try:
        words.remove(word)
    except:
        pass


print(len(words))
vecs = model.embed(words)
pca = PCA(n_components=10)
vecs = pca.fit_transform(vecs)
words = [right_pad(w) for w in words]
serde_bin_vec.save_all(zip(words, vecs), "english.vectors")
