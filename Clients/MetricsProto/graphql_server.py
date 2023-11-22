from flask import Flask, jsonify, request
import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from Clients.Db.database import Database

app = Flask(__name__)
CORS(app)

# Configure o banco de dados SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../tracking.db'
db = SQLAlchemy(app)


class Metrics(db.Model):
    __tablename__ = 'metrics'

    id = db.Column(db.Integer, primary_key=True)
    device_code = db.Column(db.String)
    day = db.Column(db.Date)
    total_positions = db.Column(db.Integer, default=0)
    total_distance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class MetricsObject(SQLAlchemyObjectType):
    class Meta:
        model = Metrics
        interfaces = (graphene.relay.Node,)


class ConsultaMetricsType(graphene.ObjectType):
    id_dispositivo = graphene.String()
    marca = graphene.String()
    quantidade_posicao = graphene.Int()
    total_km = graphene.Float()


class Query(graphene.ObjectType):
    consultaDispositivo = graphene.Field(
        ConsultaMetricsType,
        id_dispositivo=graphene.String(),
        dia=graphene.String(),
    )

    consultaMarca = graphene.Field(
        ConsultaMetricsType,
        marca=graphene.String(),
        dia=graphene.String(),
    )

    consultaGeral = graphene.Field(
        ConsultaMetricsType,
        dia=graphene.String(),
    )

    def resolve_consultaDispositivo(self, info, id_dispositivo=None, dia=None):
        # Não importa o que seja passado como argumento, sempre retornará "foi"
        return ConsultaMetricsType(
            id_dispositivo="foi",
            marca=None,
            quantidade_posicao=None,
            total_km=None,
        )

    def resolve_consultaMarca(self, info, marca=None, dia=None):
        db_instance = Database()

        if marca and dia:
            metrics_info = db_instance.consulta_marca(marca, dia)
            if metrics_info:
                return ConsultaMetricsType(
                    id_dispositivo=None,
                    marca=marca,
                    quantidade_posicao=metrics_info['quantidade_posicao'],
                    total_km=metrics_info['total_km']
                )

        return None

    def resolve_consultaGeral(self, info, dia=None):
        db_instance = Database()

        if dia:
            metrics_info = db_instance.consulta_geral(dia)
            if metrics_info:
                return ConsultaMetricsType(
                    id_dispositivo=None,
                    marca=None,
                    quantidade_posicao=metrics_info['quantidade_posicao'],
                    total_km=metrics_info['total_km']
                )

        return None


schema = graphene.Schema(query=Query)

# Rota para a API GraphQL
@app.route('/graphql', methods=['POST'])
def graphql():
    data = request.get_json(force=True)
    params = data.get('variables', {})
    query = data.get('query')
    result = schema.execute(query, variable_values=params)

    if result.errors:
        return jsonify({'errors': [str(error) for error in result.errors]}), 400

    return jsonify({'data': result.data})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
