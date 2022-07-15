import sqlite3

def deleteTableRecords():
    try: 
      sqliteConnection = sqlite3.connect('/home/pi/dhcp/staticDHCPd/dhcp.sqlite3')
      cursor = sqliteConnection.cursor()
      print("connected to SQLite")
      #id, mac, ip, hostname, subnet, serial

      truncate_query = "DELETE FROM maps"
      cursor.execute(truncate_query)
    except sqlite3.Error as error:
      print("Failed to read data from sqlite table", error)
    finally:
      if sqliteConnection:
        sqliteConnection.commit()
        sqliteConnection.close()
        print("database cleared!")
        print("The SQLite connection is closed")

deleteTableRecords()
