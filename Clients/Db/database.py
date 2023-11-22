import sqlite3
from datetime import datetime, timedelta
from sqlite3 import connect


def get_current_datetime():
    current_datetime = datetime.now()
    return current_datetime.strftime("%Y-%m-%d %H:%M:%S")


class Database:
    def __init__(self, db_file='tracking.db'):
        self.db_file = db_file

    # Location Queries
    def save_location(self, device_info):
        try:
            if not all(key in device_info for key in ['device_code', 'latitude', 'longitude']):
                raise ValueError("Algumas informações de localização estão ausentes.")

            with connect(self.db_file) as conn:
                conn.execute(
                    'INSERT INTO location (device_code, latitude, longitude) VALUES (?, ?, ?)',
                    (
                        str(device_info.get('device_code')),
                        str(device_info.get('latitude')),
                        str(device_info.get('longitude')),
                    )
                )
        except Exception as e:
            print(f"Erro ao salvar localização: {str(e)}")

    def delete_location_history(self, device_code):
        try:
            with connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM location WHERE device_code = ?', (device_code,))
        except Exception as e:
            print(f"Erro ao excluir histórico de localização: {str(e)}")

    def get_location_data(self, device_code, from_date=None, to_date=None):
        try:
            with connect(self.db_file) as conn:
                cursor = conn.cursor()

                query = 'SELECT * FROM location WHERE device_code = ?'
                parameters = [device_code]

                if from_date:
                    query += ' AND created_at >= ?'
                    parameters.append(from_date)

                if to_date:
                    query += ' AND created_at <= ?'
                    parameters.append(to_date)
                elif from_date:
                    # Se apenas from_date estiver presente, adicione a data e hora atual a to_date
                    to_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
                    query += ' AND created_at <= ?'
                    parameters.append(to_date)

                # Ordenar por data de forma decrescente
                query += ' ORDER BY created_at DESC'

                cursor.execute(query, tuple(parameters))
                location_data = cursor.fetchall()

                result_array = [{'id': row[0], 'device_code': row[1], 'latitude': row[2], 'longitude': row[3],
                                 'created_at': row[4], 'updated_at': row[5]} for row in location_data]

                return result_array
        except Exception as e:
            print(f"Erro ao obter dados de localização: {str(e)}")
            return []

    def add_device(self, device_info):
        try:
            with connect(self.db_file) as conn:
                conn.execute(
                    'INSERT INTO device (name, code, status, brand, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
                    (
                        str(device_info.get('name')),
                        str(device_info.get('code')),
                        device_info.get('status'),
                        str(device_info.get('brand')),
                        get_current_datetime(),
                        get_current_datetime()
                    )
                )
            print(f"Dispositivo adicionado com sucesso.")
        except Exception as e:
            print(f"Erro ao adicionar dispositivo: {str(e)}")

    # Device Queries
    def delete_device(self, device_code):
        try:
            with connect(self.db_file) as conn:
                conn.execute('DELETE FROM device WHERE code = ?', (device_code,))
        except Exception as e:
            print(f"Erro ao excluir dispositivo: {str(e)}")

    def update_device(self, device_code, device_info):
        try:
            with connect(self.db_file) as conn:
                conn.execute(
                    'UPDATE device SET name=?, code=?, status=?, brand=?, updated_at=? WHERE code = ?',
                    (
                        str(device_info.get('name')),
                        str(device_info.get('code')),
                        device_info.get('status'),
                        str(device_info.get('brand')),
                        get_current_datetime(),
                        device_code
                    )
                )
            print(f"Dispositivo atualizado com sucesso.")
        except Exception as e:
            print(f"Erro ao atualizar dispositivo: {str(e)}")

    def is_active_device(self, device_code):
        try:
            with connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT status FROM device WHERE code = ?', (device_code,))
                status = cursor.fetchone()
                return status[0] if status else None
        except Exception as e:
            print(f"Erro ao verificar status do dispositivo: {str(e)}")
            return None

    # New method to get metrics
    def get_metrics(self, device_code, day):
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM device WHERE code = ?', (device_code,))
                device_info = cursor.fetchone()

                if not device_info:
                    return None

                cursor.execute('SELECT * FROM metrics WHERE device_code = ? AND day = ?', (device_code, day))
                metrics_info = cursor.fetchone()

                return {
                    'device_code': device_code,
                    'brand': device_info[4],  # Assuming 'brand' is at position 4 in the 'device' table
                    'total_positions': metrics_info[3] if metrics_info else 0,
                    'total_distance': metrics_info[4] if metrics_info else 0
                }
        except Exception as e:
            print(f"Erro ao obter métricas: {str(e)}")
            return None

    def save_location_metrics(self, device_code, brand, distance):
        try:
            # Add logic to process distance and increment positions
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()

                # Check if the device exists
                cursor.execute('SELECT id FROM device WHERE code = ?', (device_code,))
                existing_device = cursor.fetchone()

                if existing_device:
                    # Update or insert metrics
                    cursor.execute(
                        'INSERT INTO metrics (device_code, day, total_positions, total_distance, created_at, updated_at) '
                        'VALUES (?, ?, 1, ?, ?, ?) '
                        'ON CONFLICT(device_code, day) DO UPDATE SET '
                        'total_positions = total_positions + 1, '
                        'total_distance = total_distance + ?, '
                        'updated_at = ?',
                        (device_code, '2023-01-01', distance, get_current_datetime(), get_current_datetime(), distance,
                         get_current_datetime())
                    )
                    print(f"Métricas de localização salvas com sucesso.")
        except Exception as e:
            print(f"Erro ao salvar métricas de localização: {str(e)}")

    def consulta_dispositivo(self, id_dispositivo=None, dia=None):
        try:
            with connect(self.db_file) as conn:
                cursor = conn.cursor()

                # Construir a query SQL
                query = 'SELECT device_code, brand, total_positions, total_distance FROM metrics WHERE 1 = 1'

                # Adicionar condições à query conforme necessário
                if id_dispositivo:
                    query += ' AND device_code = ?'
                if dia:
                    query += ' AND day = ?'

                # Executar a query com os parâmetros
                cursor.execute(query, (id_dispositivo, dia))

                # Obter o resultado da consulta
                metrics_info = cursor.fetchone()

                if metrics_info:
                    return {
                        'id_dispositivo': metrics_info[0],  # Substitua pelo nome real do campo na tabela Metrics
                        'marca': metrics_info[1],  # Substitua pelo nome real do campo na tabela Metrics
                        'quantidade_posicao': metrics_info[2],
                        'total_km': metrics_info[3]
                    }
                else:
                    return None

        except Exception as e:
            print(f"Erro ao consultar métricas: {str(e)}")
            return None

    def consulta_marca(self, marca=None, dia=None):
        try:
            with connect(self.db_file) as conn:
                cursor = conn.cursor()

                # Construir a query SQL
                query = 'SELECT COUNT(DISTINCT device_code) as quantidade_dispositivo, ' \
                        'brand as marca, ' \
                        'SUM(total_positions) as quantidade_posicao, ' \
                        'SUM(total_distance) as total_km ' \
                        'FROM metrics WHERE 1 = 1'

                # Adicionar condições à query conforme necessário
                if marca:
                    query += ' AND brand = ?'
                if dia:
                    query += ' AND day = ?'

                # Adicionar agrupamento e ordenação
                query += ' GROUP BY brand ORDER BY brand'

                # Executar a query com os parâmetros
                cursor.execute(query, (marca, dia))

                # Obter o resultado da consulta
                metrics_info = cursor.fetchone()

                if metrics_info:
                    return {
                        'quantidade_dispositivo': metrics_info[0],
                        'marca': metrics_info[1],
                        'quantidade_posicao': metrics_info[2],
                        'total_km': metrics_info[3]
                    }
                else:
                    return None

        except Exception as e:
            print(f"Erro ao consultar métricas por marca: {str(e)}")
            return None

    def consulta_geral(self, dia=None):
        try:
            with connect(self.db_file) as conn:
                cursor = conn.cursor()

                # Construir a query SQL
                query = 'SELECT COUNT(DISTINCT device_code) as quantidade_dispositivo, ' \
                        'SUM(total_positions) as quantidade_posicao, ' \
                        'SUM(total_distance) as total_km ' \
                        'FROM metrics WHERE 1 = 1'

                # Adicionar condição à query conforme necessário
                if dia:
                    query += ' AND day = ?'

                # Executar a query com os parâmetros
                cursor.execute(query, (dia,))

                # Obter o resultado da consulta
                metrics_info = cursor.fetchone()

                if metrics_info:
                    return {
                        'quantidade_dispositivo': metrics_info[0],
                        'quantidade_posicao': metrics_info[1],
                        'total_km': metrics_info[2]
                    }
                else:
                    return None

        except Exception as e:
            print(f"Erro ao consultar métricas gerais: {str(e)}")
            return None
