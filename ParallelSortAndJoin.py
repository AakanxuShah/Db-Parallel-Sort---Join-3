#!/usr/bin/python2.7
#
# CSE 592
# Author : Aakanxu Shah
#

import psycopg2
import os
import sys
import threading

##################### This needs to changed based on what kind of table we want to sort. ##################
##################### To know how to change this, see Assignment 3 Instructions carefully #################
FIRST_TABLE_NAME = 'table1'
SECOND_TABLE_NAME = 'table2'
SORT_COLUMN_NAME_FIRST_TABLE = 'column1'
SORT_COLUMN_NAME_SECOND_TABLE = 'column2'
JOIN_COLUMN_NAME_FIRST_TABLE = 'column1'
JOIN_COLUMN_NAME_SECOND_TABLE = 'column2'
##########################################################################################################


# Donot close the connection inside this file i.e. do not perform openconnection.close()
def ParallelSort (InputTable, SortingColumnName, OutputTable, openconnection):

    try:
        # Getting cursor of openconnection
        cur = openconnection.cursor()

        #Gets the range and mininum value of range from function Range
        interval_sort, rangeMin = Range(InputTable,SortingColumnName,openconnection)
        
        #gets the schema of InputTable
        cur.execute("SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='" + InputTable + "'")
        schema = cur.fetchall()

        #tables to store and sort range partitions    
        for i in range(5):
            
            tableName = "range_part" + str(i)
            cur.execute("DROP TABLE IF EXISTS " + tableName + "")
            cur.execute("CREATE TABLE " + tableName + " ("+schema[0][0]+" "+schema[0][1]+")")
	
            for d in range(1, len(schema)):
                cur.execute("ALTER TABLE " + tableName + " ADD COLUMN " + schema[d][0] + " " + schema[d][1] + ";")
          
                
        #create five threads
        thread = [0,0,0,0,0]
        for i in range(5):

            if i == 0:
                lowerValue = rangeMin
                upperValue = rangeMin + interval_sort
            else:
                lowerValue = upperValue
                upperValue = upperValue + interval_sort
                
            
            thread[i] = threading.Thread(target=range_insert_sort, args=(InputTable, SortingColumnName, i, lowerValue, upperValue, openconnection))
    
            thread[i].start()

        for p in range(0,5):
            thread[i].join()
    
        
        # Combine all sorted partion to OutputTable

        cur.execute("DROP TABLE IF EXISTS " + OutputTable + "")
        cur.execute("CREATE TABLE " + OutputTable + " ("+schema[0][0]+" "+schema[0][1]+")")
	
        for i in range(1, len(schema)):

            cur.execute("ALTER TABLE " + OutputTable + " ADD COLUMN " + schema[i][0] + " " + schema[i][1] + ";")

        for i in range(5):
             
            query = "INSERT INTO " + OutputTable + " SELECT * FROM " + "range_part" + str(i) + ""
            cur.execute(query)

    except Exception as message:
        print "Exception :", message

    # Clean up 
    finally:
        
        for i in range(5):
            tableName = "range_part" + str(i)
            cur.execute("DROP TABLE IF EXISTS " + tableName + "")
        cur.close()
        

def Range(InputTable, SortingColumnName,openconnection):
    cur = openconnection.cursor()

    # Gets maximum and min value of SortingColumnName
    cur.execute("SELECT MIN(" + SortingColumnName + ") FROM " + InputTable + "")
    MinVal=cur.fetchone()
    range_min_value = (float)(MinVal[0])
    
    cur.execute("SELECT MAX(" + SortingColumnName + ") FROM " + InputTable + "")
    MaxVal=cur.fetchone()
    range_max_value = (float)(MaxVal[0])
    
    interval = (range_max_value - range_min_value)/5
    return interval , range_min_value


# Inserts in sorted value 
def range_insert_sort(InputTable, SortingColumnName, index, min_val, max_val, openconnection):

    cur=openconnection.cursor()

    table_name = "range_part" + str(index)

    # Check for minimum value of column
    if index == 0:
        query = "INSERT INTO " + table_name + " SELECT * FROM " + InputTable + "  WHERE " + SortingColumnName + ">=" + str(min_val) + " AND " + SortingColumnName + " <= " + str(max_val) + " ORDER BY " + SortingColumnName + " ASC"
    else:
        query = "INSERT INTO " + table_name + " SELECT * FROM " + InputTable + "  WHERE " + SortingColumnName + ">" + str(min_val) + " AND " + SortingColumnName + " <= " + str(max_val) + " ORDER BY " + SortingColumnName + " ASC"

    cur.execute(query)
    cur.close()
    return

########################################-- END OF PARALLEL SORT--###########################################################

def MinMax(InputTable1, InputTable2 , Table1JoinColumn , Table2JoinColumn, openconnection):
    # Getting cursor of openconnection
        cur = openconnection.cursor()

	# Gets maximum and min value of column
        cur.execute("SELECT MIN(" + Table1JoinColumn + ") FROM " + InputTable1 + "")
        minimum1=cur.fetchone()
        Min1 = (float)(minimum1[0])

        cur.execute("SELECT MIN(" + Table2JoinColumn + ") FROM " + InputTable2 + "")
        minimum2=cur.fetchone()
        Min2 = (float)(minimum2[0])
	
        cur.execute("SELECT MAX(" + Table1JoinColumn + ") FROM " + InputTable1 + "")
        maximum1=cur.fetchone()
        Max1 = (float)(maximum1[0])

        cur.execute("SELECT MAX(" + Table2JoinColumn + ") FROM " + InputTable2 + "")
        maximum2=cur.fetchone()
        Max2 = (float)(maximum2[0])

        if Max1 > Max2:
            rangeMax = Max1
        else:
            rangeMax = Max2

        if Min1 > Min2:
            rangeMin = Min2
        else:
            rangeMin = Min1    

        interval = (rangeMax - rangeMin)/5

        return interval , rangeMin

def OutputRangeTable(InputTable1, InputTable2, Table1JoinColumn, Table2JoinColumn, schema1 , schema2 , interval , range_min_value, openconnection):
    cur = openconnection.cursor();
    for i in range(5):

            range_table1_name = "table1_range" + str(i)
            range_table2_name = "table2_range" + str(i)

            if i==0:
                lowerValue = range_min_value
                upperValue = range_min_value + interval
            else:
                lowerValue = upperValue
                upperValue = upperValue + interval

            cur.execute("DROP TABLE IF EXISTS " + range_table1_name + ";")
            cur.execute("DROP TABLE IF EXISTS " + range_table2_name + ";")

            if i == 0:
                cur.execute("CREATE TABLE " + range_table1_name + " AS SELECT * FROM " + InputTable1 + " WHERE (" + Table1JoinColumn + " >= " + str(lowerValue) + ") AND (" + Table1JoinColumn + " <= " + str(upperValue) + ");")
                cur.execute("CREATE TABLE " + range_table2_name + " AS SELECT * FROM " + InputTable2 + " WHERE (" + Table2JoinColumn + " >= " + str(lowerValue) + ") AND (" + Table2JoinColumn + " <= " + str(upperValue) + ");")
                
            else:
                cur.execute("CREATE TABLE " + range_table1_name + " AS SELECT * FROM " + InputTable1 + " WHERE (" + Table1JoinColumn + " > " + str(lowerValue) + ") AND (" + Table1JoinColumn + " <= " + str(upperValue) + ");")
                cur.execute("CREATE TABLE " + range_table2_name + " AS SELECT * FROM " + InputTable2 + " WHERE (" + Table2JoinColumn + " > " + str(lowerValue) + ") AND (" + Table2JoinColumn + " <= " + str(upperValue) + ");")

           
	    # Output range table
            output_range_table = "output_table" + str(i)

            cur.execute("DROP TABLE IF EXISTS " + output_range_table + "")
            cur.execute("CREATE TABLE " + output_range_table + " ("+schema1[0][0]+" "+schema2[0][1]+")")

            for j in range(1, len(schema1)):

                cur.execute("ALTER TABLE " + output_range_table + " ADD COLUMN " + schema1[j][0] + " " + schema1[j][1] + ";")

            for j in range(len(schema2)):

                cur.execute("ALTER TABLE " + output_range_table + " ADD COLUMN " + schema2[j][0] + "1" +" "+ schema2[j][1] + ";")
    
    

def ParallelJoin (InputTable1, InputTable2, Table1JoinColumn, Table2JoinColumn, OutputTable, openconnection):

    try:
	# Getting cursor of openconnection
        cur = openconnection.cursor()

        interval , range_min_value = MinMax(InputTable1, InputTable2 , Table1JoinColumn , Table2JoinColumn, openconnection)

        # Get schemas of input tables
        cur.execute("SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='" + InputTable1 + "'")
        schema1 = cur.fetchall()

        cur.execute("SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='" + InputTable2 + "'")
        schema2 = cur.fetchall()

        #output table
        cur.execute("DROP TABLE IF EXISTS " + OutputTable + "")
        cur.execute("CREATE TABLE " + OutputTable + " ("+schema1[0][0]+" "+schema2[0][1]+")")

        for i in range(1, len(schema1)):

            cur.execute("ALTER TABLE " + OutputTable + " ADD COLUMN " + schema1[i][0] + " " + schema1[i][1] + ";")

        for i in range(len(schema2)):

            cur.execute("ALTER TABLE " + OutputTable + " ADD COLUMN " + schema2[i][0] + "1" +" " + schema2[i][1] + ";")


	
	# Calls the OuputRangeTable function for temporary output range table

        OutputRangeTable(InputTable1, InputTable2, Table1JoinColumn, Table2JoinColumn, schema1, schema2 , interval , range_min_value, openconnection)


	# Creats five threads
        thread = [0,0,0,0,0]

        for i in range(5):

            thread[i] = threading.Thread(target=range_insert_join, args=(Table1JoinColumn, Table2JoinColumn, openconnection, i))

            thread[i].start()
            
        for a in range(0,5):
            thread[i].join()

	# Inserts in output table
        for i in range(5):

            cur.execute("INSERT INTO " + OutputTable + " SELECT * FROM output_table" + str(i))
	
    except Exception as detail:
        print "Exception in ParallelJoin is ==>>", detail

    # Clean up
    finally:
        for i in range(5):
            cur.execute("DROP TABLE IF EXISTS table1_range" + str(i))
            cur.execute("DROP TABLE IF EXISTS table2_range" + str(i))
            cur.execute("DROP TABLE IF EXISTS output_table" + str(i))

        cur.close()


def range_insert_join(Table1JoinColumn, Table2JoinColumn, openconnection, TempTableId):
	
    cur=openconnection.cursor()

    query = "INSERT INTO output_table" + str(TempTableId) + " SELECT * FROM table1_range" + str(TempTableId) + " INNER JOIN table2_range" + str(TempTableId) + " ON table1_range" + str(TempTableId) + "." + Table1JoinColumn + "=" + "table2_range" + str(TempTableId) + "." + Table2JoinColumn + ";"

    cur.execute(query)
    cur.close()
    return




################### DO NOT CHANGE ANYTHING BELOW THIS #############################


# Donot change this function
def getOpenConnection(user='postgres', password='1234', dbname='ddsassignment3'):
    return psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='localhost' password='" + password + "'")

# Donot change this function
def createDB(dbname='ddsassignment3'):
    """
    We create a DB by connecting to the default user and database of Postgres
    The function first checks if an existing database exists for a given name, else creates it.
    :return:None
    """
    # Connect to the default database
    con = getOpenConnection(dbname='postgres')
    con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()

    # Check if an existing database with the same name exists
    cur.execute('SELECT COUNT(*) FROM pg_catalog.pg_database WHERE datname=\'%s\'' % (dbname,))
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute('CREATE DATABASE %s' % (dbname,))  # Create the database
    else:
        print 'A database named {0} already exists'.format(dbname)

    # Clean up
    cur.close()
    con.commit()
    con.close()

# Donot change this function
def deleteTables(ratingstablename, openconnection):
    try:
        cursor = openconnection.cursor()
        if ratingstablename.upper() == 'ALL':
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = cursor.fetchall()
            for table_name in tables:
                cursor.execute('DROP TABLE %s CASCADE' % (table_name[0]))
        else:
            cursor.execute('DROP TABLE %s CASCADE' % (ratingstablename))
        openconnection.commit()
    except psycopg2.DatabaseError, e:
        if openconnection:
            openconnection.rollback()
        print 'Error %s' % e
        sys.exit(1)
    except IOError, e:
        if openconnection:
            conn.rollback()
        print 'Error %s' % e
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()

# Donot change this function
def saveTable(ratingstablename, fileName, openconnection):
    try:
        cursor = openconnection.cursor()
        cursor.execute("Select * from %s" %(ratingstablename))
        data = cursor.fetchall()
        openFile = open(fileName, "w")
        for row in data:
            for d in row:
                openFile.write(`d`+",")
            openFile.write('\n')
        openFile.close()
    except psycopg2.DatabaseError, e:
        if openconnection:
            openconnection.rollback()
        print 'Error %s' % e
        sys.exit(1)
    except IOError, e:
        if openconnection:
            conn.rollback()
        print 'Error %s' % e
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()

if __name__ == '__main__':
    try:
	# Creating Database ddsassignment2
        print "Creating Database named as ddsassignment2"
        createDB();
	
	# Getting connection to the database
        print "Getting connection from the ddsassignment2 database"
        con = getOpenConnection();

	# Calling ParallelSort
        print "Performing Parallel Sort"
        ParallelSort(FIRST_TABLE_NAME, SORT_COLUMN_NAME_FIRST_TABLE, 'parallelSortOutputTable', con);

	# Calling ParallelJoin
        print "Performing Parallel Join"
        ParallelJoin(FIRST_TABLE_NAME, SECOND_TABLE_NAME, JOIN_COLUMN_NAME_FIRST_TABLE, JOIN_COLUMN_NAME_SECOND_TABLE, 'parallelJoinOutputTable', con);
	
	# Saving parallelSortOutputTable and parallelJoinOutputTable on two files
        saveTable('parallelSortOutputTable', 'parallelSortOutputTable.txt', con);
        saveTable('parallelJoinOutputTable', 'parallelJoinOutputTable.txt', con);

	# Deleting parallelSortOutputTable and parallelJoinOutputTable
        deleteTables('parallelSortOutputTable', con);
        deleteTables('parallelJoinOutputTable', con);

        if con:
            con.close()

    except Exception as detail:
        print "Something bad has happened!!! This is the error ==> ", detail
        
#Disclaimer for students: Be Original and do not Plagarize ! :) 
