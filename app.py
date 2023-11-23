from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import boto3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fruits.db'
db = SQLAlchemy(app)

personalize_runtime = boto3.client('personalize-runtime', region_name='ap-northeast-1')

class Fruit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Fruit %r>' % self.name

def init_fruits(db):
    fruits = ['Apple', 'Banana', 'Orange', 'Strawberry', 'Blueberry', 'Mango',
              'Pineapple', 'Watermelon', 'Grapefruit', 'Lemon', 'Lime', 'Cherry',
              'Grape', 'Melon', 'Kiwi', 'Peach', 'Nectarine', 'Papaya', 'Guava',
              'Lingonberry', 'Raspberry', 'Blackberry', 'Apricot', 'Plum',
              'Passion Fruit', 'Avocado', 'Persimmon', 'Pomegranate',
              'Dragon Fruit', 'Fig']  # ここに30種類のフルーツをリストとして追加
    existing_fruits = Fruit.query.all()
    if not existing_fruits:
        for fruit_name in fruits:
            fruit = Fruit(name=fruit_name)
            db.session.add(fruit)
        db.session.commit()

with app.app_context():
    db.create_all()
    # 初期フルーツデータの追加
    init_fruits(db)

def get_personalize_recommendations(user_id):
    response = personalize_runtime.get_recommendations(
        campaignArn="arn:aws:personalize:ap-northeast-1:538815528650:campaign/saitou-handson-campaign",
        userId=str(user_id)
    )
    item_ids = [int(item['itemId']) for item in response['itemList']]
    return item_ids


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_id_input = request.form['userid']
        # ユーザーIDが整数かどうかを検証
        if user_id_input.isdigit():
            user_id = int(user_id_input)
            item_ids = get_personalize_recommendations(user_id)
            # データベースからフルーツの名前を取得
            fruits = [Fruit.query.get(item_id).name for item_id in item_ids]
            return render_template('welcome.html', user_id=user_id, fruits=fruits)
        else:
            error_message = "ユーザーIDは整数である必要があります。"
            return render_template('index.html', error=error_message)

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)