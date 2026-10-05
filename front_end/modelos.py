"""Carrega os modelos exportados e preserva a representação utilizada no treino."""

import hashlib
import json
from pathlib import Path

import joblib
import pandas as pd
import sklearn

from front_end.jogo import CLASSES, extrair_entradas


MODELOS = {
    "mlp": ("MLP · rede neural", "mlp", "mlp.ipynb"),
    "svm": ("SVM · vetores de suporte", "svm", "svm.ipynb"),
    "knn": ("k-NN · vizinhos mais próximos", "knn", "knn.ipynb"),
    "arvore": ("Árvore de decisão", "arvoreDecisao", "arvore_decisao.ipynb"),
    "random_forest": ("Random Forest · floresta aleatória", "randomForest", "random_forest.ipynb"),
}


class Classificadores:
    def __init__(self, raiz):
        self.pipelines = {}
        self.informacoes = {}
        for chave, (nome, diretorio, notebook) in MODELOS.items():
            pasta = Path(raiz) / "dataset/processado" / diretorio / "resultados"
            arquivo = pasta / f"modelo_{chave}.joblib"
            caminho_notebook = f"dataset/processado/{diretorio}/{notebook}"
            if not arquivo.is_file() or not (pasta / "resumo_experimento.json").is_file():
                raise ValueError(f"Execute a última etapa de {caminho_notebook} para exportar seu modelo.")
            try:
                resumo = json.loads((pasta / "resumo_experimento.json").read_text(encoding="utf-8"))
            except json.JSONDecodeError as erro:
                raise ValueError(f"O resumo do modelo {chave} não é um JSON válido.") from erro
            versao = resumo["versoes"]["scikit_learn"]
            if sklearn.__version__ != versao:
                raise ValueError(
                    f"O modelo {chave} foi salvo com scikit-learn {versao}, "
                    f"mas este Python usa {sklearn.__version__}. Execute o front end no mesmo "
                    "ambiente dos notebooks, ou execute os notebooks novamente neste ambiente."
                )
            pipeline = joblib.load(arquivo)
            if set(pipeline.classes_) != set(CLASSES):
                raise ValueError(f"O modelo {chave} precisa prever as quatro classes do trabalho.")
            abordagem = resumo["abordagem_escolhida_pela_validacao"]
            colunas = resumo["features_modelo_exportado"]
            if list(pipeline.feature_names_in_) != colunas:
                raise ValueError(f"As colunas registradas para {chave} não correspondem ao modelo salvo.")
            if set(extrair_entradas(["b"] * 9, abordagem)) != set(colunas):
                raise ValueError(f"A representação de entrada do modelo {chave} é desconhecida.")
            self.pipelines[chave] = pipeline
            self.informacoes[chave] = {
                "nome": nome, "abordagem": abordagem, "features": colunas,
                "versao_scikit_learn": versao,
                "modelo_sha256": hashlib.sha256(arquivo.read_bytes()).hexdigest(),
            }

    def prever(self, modelo, tabuleiro):
        """Classifica o tabuleiro usando o pré-processamento e o modelo já ajustados."""
        info = self.informacoes[modelo]
        entradas = extrair_entradas(tabuleiro, info["abordagem"])
        # Reutiliza o modelo e, quando presente, o padronizador ajustado no treino.
        X = pd.DataFrame([entradas], columns=info["features"])
        return str(self.pipelines[modelo].predict(X)[0])
