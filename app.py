import json
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from datetime import datetime as dt


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]='postgresql://postgres:postgres@localhost/bills'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db=SQLAlchemy(app)

class Bill(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    date = db.Column(db.DateTime(),nullable=False)
    num=db.Column(db.String(12), nullable=False)
    description=db.Column(db.Text(), nullable=False)
    
    def __repr__(self):
        return self.num
    
    @classmethod
    def get_all(cls):
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    
    def  save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
class BillSchema(Schema):
    id=fields.Integer()
    date=fields.DateTime()
    num=fields.String()
    description=fields.String()
            
        

@app.route('/bills', methods=['GET'])
def get_all_bills():
    bills=Bill.get_all()
    
    serializer=BillSchema(many=True)
    data=serializer.dump(bills)
    return jsonify(
        data
    )

@app.route('/bill', methods=['POST'])
def create_a_bill():
    data=request.get_json()
    new_bill=Bill(
        num=data.get('num'),
        date=dt.now(),
        description=data.get('description')
    )
    new_bill.save()
    serializer=BillSchema()
    data=serializer.dump(new_bill)
    
    return jsonify(
        data
    ),201
    
@app.route('/bill/<int:id>', methods=['GET'])
def get_bill(id):
    bill=Bill.get_by_id(id)
    
    serializer = BillSchema()
    data = serializer.dump(bill)
    return jsonify(
        data
    ),200
    
@app.route('/bill/<int:id>',methods=['PUT'])
def update_bill(id):
    bill_to_update=Bill.get_by_id(id)
    
    data=request.get_json()
    bill_to_update.num=data.get('num')
    bill_to_update.description=data.get('description')
    
    db.session.commit()
    serializer=BillSchema()
    bill_data=serializer.dump(bill_to_update)
    return jsonify(bill_data),200
    
@app.route('/bill/<int:id>', methods=['DELETE'])
def delete_bill(id):
    bill_to_delete=Bill.get_by_id(id)
    
    bill_to_delete.delete()
    return jsonify({"Message":"Deleted"}),204

@app.errorhandler(404)
def not_found(error):
    return jsonify({"message":"Not found"}),404


@app.errorhandler(500)
def internal_server(error):
    return jsonify({"message":"There is a problem"}),500


if __name__ == '__main__':
    app.run(debug=True)