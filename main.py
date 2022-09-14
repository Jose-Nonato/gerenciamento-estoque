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

#### Listagem dos Produtos Disponiveis no Estoque ####
@app.route("/")
def dataList():
    consulta = list(db.Produtos.find())
    return render_template("index.html", consulta=consulta)

#### Adicionar Produto ao Estoque ####
@app.route("/create", methods=["POST", "GET"])
def create_product():
    msg = ''
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

        try:
            db.Produtos.insert_one(produto)
        except:
            msg = f"O produto com o id {codigo} já existe!\nCrie com outro código!"
            return render_template("alertas.html", msg=msg)

        return redirect("/")

    return render_template("create.html")

#### Atualizando produto do estoque ####
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


#### Deletando Produto do Estoque ####
@app.route("/delete/<int:id>", methods=["POST", "GET"])
def deleteProduct(id):
    consulta = db.Produtos.find_one({"_id": id})
    if request.method == "POST":
        if consulta:
            db.Produtos.delete_one(consulta)
            return redirect("/")
    return render_template("delete.html")

#### Carrinho de Compras ###
@app.route("/cart", methods=["GET", "POST"])
def cart():
    produtos = db.Produtos.find()
    if request.method == "POST":
        codigo = int(request.form.get("codigo"))
        quantidade = int(request.form.get("quantidade"))
        consulta = db.Produtos.find_one({"_id": codigo})
        if consulta:
            try:
                db.Carrinho.insert_one({"_id": codigo, "quantidade": quantidade})
                c1 = list(db.Produtos.find())
                c2 = list(db.Carrinho.find())
                for cart in c2:
                    for prod in c1:
                        if cart['_id'] == prod['_id']:
                            db.Carrinho.update_one(
                                {'_id': cart['_id']},
                                {'$set': {'total': cart['quantidade'] * prod['preco']}},
                            )
            except:
                msg = f"{codigo} já está adicionado no carrinho."
                return render_template("alertas.html", msg=msg)
        else:
            msg = f"O produto com o código {codigo} não existe na base!"
            return render_template("alertas.html", msg=msg)
    return render_template("cart.html", produtos=produtos)

#### Carrinho de Compras Final ####
@app.route("/cart/items", methods=["POST", "GET"])
def cartItems():
    consultaCarrinho = list(db.Carrinho.find())
    consultaBase = list(db.Produtos.find())

    total = 0.0
    for i in consultaCarrinho:
        total += i['total']

    if request.method == "POST":
        c1 = list(db.Produtos.find())
        c2 = list(db.Carrinho.find())
        for cart in c2:
            for prod in c1:
                if cart['_id'] == prod['_id']:
                    db.Produtos.update_one(
                        {'_id': cart['_id']},
                        {'$set': {'quantidade': prod['quantidade'] - cart['quantidade'], 'total': (prod['quantidade'] - cart['quantidade'])  * prod['preco']}}
                    )
        db.Carrinho.drop()
        return redirect("/cart")

    return render_template("cartItems.html", consultaCarrinho=consultaCarrinho, consultaBase=consultaBase, total=total)


#### Deletando Produto do Carrinho de Compras ####
@app.route("/cart/items/delete/<int:id>", methods=["POST", "GET"])
def deleteCartItem(id):
    consulta = db.Carrinho.find_one({"_id": id})
    if request.method == "POST":
        if consulta:
            db.Carrinho.delete_one(consulta)
            return redirect("/")
    return render_template("delete.html")

if __name__ == "__main__":
    app.run(debug=True)