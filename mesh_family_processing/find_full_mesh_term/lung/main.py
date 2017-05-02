#!/usr/bin/python

from urllib.parse import quote
import difflib
import math
import pymysql
import sys
import time

get_current_millis = lambda: int(round(time.time() * 1000))
def get_elapsed_seconds(current_time, elapsed_millis):
  return (current_time - elapsed_millis) / 1000.0

START_S_ID = None
if len(sys.argv) > 1:
  START_S_ID = sys.argv[1]

db = pymysql.connect(host='localhost', user='root', password='', db='mesh', charset='utf8')

elapsed_millis = get_current_millis()
# Get all genes in DB.
all_genes = None
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  query = 'SELECT * FROM LUNG_GENES ORDER BY S_ID' if START_S_ID is None \
    else 'SELECT * FROM LUNG_GENES WHERE S_ID > %s ORDER BY S_ID' % (START_S_ID)
  cursor.execute(query)
  all_genes = cursor.fetchall()
print('Find all genes time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))

# Find full mesh term
values = []
for gene in all_genes:
  elapsed_millis = get_current_millis()
  processeds = None
  with db.cursor(pymysql.cursors.DictCursor) as cursor:
    cursor.execute('SELECT * FROM LUNG_PROCESSED where S_ID = %s', (gene['S_ID'],))
    processeds = cursor.fetchall()
  print('Find processeds time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))
  
  full_mesh_term = max(processeds, key=lambda processed: len(processed['P_NAME']))['P_NAME']
  
  print('UPDATE LUNG_GENES SET MESH_TERM=%s WHERE S_ID=%s' % (
    full_mesh_term, gene['S_ID']))
  values.append([gene['S_ID'], full_mesh_term])

elapsed_millis = get_current_millis()
# Send a query to update LUNG_GENES.
with db.cursor(pymysql.cursors.DictCursor) as cursor:
  cursor.executemany(
    'INSERT INTO LUNG_GENES (S_ID, MESH_TERM) VALUES (%s, %s) ON DUPLICATE KEY UPDATE MESH_TERM=VALUES(MESH_TERM)',
    values
  )
db.commit()
print('Update gene time:', get_elapsed_seconds(get_current_millis(), elapsed_millis))