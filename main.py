from flask import Flask, render_template, request, redirect
import pymongo

app = Flask(__name__)

class Produto:
    ''' Abstraindo um produto para a criação do objeto Produto de uma loja '''
    nome = ""
    marca = ""
    quantidade = ""
    preco = ""
    codigo = ""

    #### Getters e Setters ####
    def setNome(self, nome):
        self.nome = nome
    def getNome(self):
        return self.nome
    def setMarca(self, marca):
        self.marca = marca
    def getMarca(self):
        return self.marca
    def setQuantidade(self, qtd):
        self.quantidade = qtd
    def getQuantidade(self):
        return self.quantidade
    def setPreco(self, preco):
        self.preco = preco
    def getPreco(self):
        return self.preco
    def setCodigo(self, codigo):
        self.codigo = codigo
    def getCodigo(self):
        return self.codigo

try:
    mongo = pymongo.MongoClient("mongodb://localhost:27017/")
    db = mongo.topsexy
    mongo.server_info()
except:
    print("ERROR -Cannot connect to DB")

#### Listagem dos Produtos ####
@app.route("/")
def dataList():
    consulta = list(db.Produtos.find())
    return render_template("index.html", consulta=consulta)

#### Criar Produto ####
@app.route("/create", methods=["POST", "GET"])
def create_product():
    if request.method == "POST":
        codigo = request.form.get("codigo")
        nome = request.form.get("nome")
        marca = request.form.get("marca")
        quantidade = request.form.get("quantidade")
        preco = request.form.get("preco")

        p = Produto()
        p.setCodigo(codigo)
        p.setNome(nome)
        p.setMarca(marca)
        p.setQuantidade(quantidade)
        p.setPreco(preco)

        produto = { "_id": int(p.getCodigo()), "produto": p.getNome(), "marca": p.getMarca(), "quantidade": int(p.getQuantidade()), "preco": float(p.getPreco()), "total": float(p.getPreco()) * int(p.getQuantidade())  }

        db.Produtos.insert_one(produto)

        return redirect("/")

    return render_template("create.html")

@app.route("/update/<int:id>", methods=["POST", "GET"])
def updateProduct(id):
    consulta = db.Produtos.find_one({"_id": id})
    if request.method == "POST":
        if consulta:
            nome = request.form.get("nome")
            marca = request.form.get("marca")
            quantidade = request.form.get("quantidade")
            preco = request.form.get("preco")

            db.Produtos.update_one(
                { "_id": id },
                {"$set": { "produto": nome, "marca": marca, "quantidade": int(quantidade), "preco": float(preco), "total": int(quantidade) * float(preco) } }
            )

            return redirect("/")
        return f"Produto com o id {id} não existe!"

    return render_template("update.html", consulta=consulta)

@app.route("/delete/<int:id>", methods=["POST", "GET"])
def deleteProduct(id):
    consulta = db.Produtos.find_one({"_id": id})
    if request.method == "POST":
        if consulta:
            db.Produtos.delete_one(consulta)
            return redirect("/")
    return render_template("delete.html")

if __name__ == "__main__":
    app.run(debug=True)