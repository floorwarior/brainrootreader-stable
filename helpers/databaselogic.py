import sqlite3
import json
import datetime
import os



class dbModel():
    """
    *db_name* name of the file where your database lives or will live
    *table name* name of the table you want to use, note that a dbmodel only ever works on one table at a time
    *col names* name of the columns of your database
    *col type* one of TEXT, BLOB, INTEGER, REAL, NULL
    usage:
    ```
    new_db_table = dbModel(
        db_name = "example.db",
        table_name = "users",
        col_names=["username","salary"],
        col_type = ["TEXT","REAL"]
    )
    ```
    """

    def __init__(self,db_name,table_name,col_names,col_type,special=False,db_folder=os.getcwd()):
        self.db_name = db_name
        self.table_name = table_name
        self.col_names = col_names
        self.db_folder = db_folder
        self.col_type = col_type
        self.legaltypes = ["TEXT","BLOB","INTEGER","REAL","NULL"]
        if self.__check_if_table():
            print(f"The table: {self.table_name} already exists")
        else:
            print(f"This table: {self.table_name} doesnt not exists yet, creating now:")
            self.create_table(confirm=False)


    def create_table(self,confirm=True):
        """creates the table the new version will call this automaticly to create your table if it does not exist yet"""
        if confirm ==  True:
            if input(f"Are you sure you want to create this table? {self.table_name} [ yes | any ]: ") != "yes":
                return False
        cursor,connector = self.get_connection()
        cols = ",".join([f"{col} {type_}" for col,type_ in zip(self.col_names,self.col_type)]) # this frst creates the col its type and goes over all the cols you specified
        thelinewerunning = f"""CREATE TABLE  {self.table_name}({cols}
        );"""

        print("Creating table with:",thelinewerunning)
        cursor.execute(thelinewerunning)
        connector.commit()
        cursor.close()
        return True
    


    def find_where(self,col_name=["username"], conditions=[],strict=True,getall=True,onecol=False,prefered_key=None,values=[]):
        """
        **Params**
        - col_name -> which col you looking for: example username update it should take more then one item
        - conditions [ "col operator value", . . . ]
        - if there is no condition it simply returns all, that is the matching by first selector
        - getall will return all matching items
        - strict checks you conditions in a chain rather then with an or if or is used we get everything
        - if getall is false you get one row
        - if one col is true you will only get the one col without a tuple
        - prefered key: if you get more that one items and not all cols are uniqe it might come handy, if left as none it will pick the first col that you look for
        - otherwise it will use the specified col as the key

    
        `SELECT <col_name goes here> FROM users WHERE <conditions go here: status = 'active'> ;`
        """
        if not all([(col in self.col_names) or (col == "*") for col in col_name]):
            raise BaseException(f"column missmatch? this is what you searched for: {col_name}")
        

        if getall:print("find where is running with GETALL make sure this is correct and you are lookig for all valid elements")

        #if col_name not in self.col_names and col_name != "*":
        #    raise BaseException(f"column missmatch? this is what you searched for: {col_name}")


        cursor,connector = self.get_connection()
        conditionalstring = " AND ".join(conditions) if strict else " OR ".join(conditions)
        thisiswhatweexecuting = f"""SELECT {','.join(col_name)} FROM {self.table_name} {'WHERE' if conditions != [] else ''} {conditionalstring};"""
        print(thisiswhatweexecuting)
        cursor.execute(thisiswhatweexecuting,values)
        temp_dict={}


        
        if getall:
            values = cursor.fetchall()
            for row in values:
                oneuser = {key:val for key,val in zip(col_name,row)}
                if prefered_key:
                    pref_key = oneuser.get(prefered_key)
                else:
                    pref_key = row[0]
                temp_dict[pref_key] = {key:val for key,val in zip(col_name,row)}

        if not getall:
            values = cursor.fetchone()
            if values and values != []:
                #print(values)
                temp_dict = {key:val for key,val in list(zip(col_name,values))}       
        connector.commit()
        cursor.close()
        connector.close()
        return temp_dict



    def exec_any(self,command,values,confirm=False):
        """executes any and command supplied with any and all values"""

        if confirm:
            if not input("are you sure you want to execute: (y/any):").lower() == "y":
                return False

        cursor,connector = self.get_connection()
        print("Exec any is running with:",command)
        cursor.execute(command,values)
        # take data and return it
        matches = cursor.fetchall()


        connector.commit()
        cursor.close()
        connector.close()
        return matches


    def get_connection(self):
        connector = sqlite3.connect(self.db_name)
        cursor = connector.cursor()

        return cursor,connector

    def __check_if_table(self):
        """cheks to see if a table is present or it does not exists"""
        command = f"SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        res = self.exec_any(command,values=[self.table_name])
        if res:
            return True
        return False

    def update(self,col_name,col_val,what,to):
        """
        example:
        UPDATE users SET age = 31 WHERE name = 'Alice';
        col_name -> name 
        col_val -> Alice
        what -> age
        to -> 31
        this should only be used with the primary key which is the username right now
        the col name and col value are indentifying the thing to update
        if the col and its value are not uniqe it will update that as well        


        """
        cursor,connector = self.get_connection()
        lineweexecute = f"""UPDATE {self.table_name} SET {what} = ? WHERE {col_name} = ?;"""
        print("updating with:",lineweexecute)
        success = False
        try:
            cursor.execute(lineweexecute,[to,col_val])
            connector.commit()
            success = True
        except Exception as e:
            print(f"failed updating user: {str(col_val)[:100]} in {col_name} , because: {e}")
            success = False
        finally:
            cursor.close()
            return success




    def multi_update(self,datadict:dict,identifier_dict:dict):
        """changes multiple values in the same time
        usage
        ```
        example_db.multi_update(datadict={
            "status":"terminated"
        },identifier_dict={
        "age":"110",
        "overtime":"0"})
        ```
        """
        keys = list(datadict.keys())
        vals = list(datadict.values()) + list(identifier_dict.values())
        placeholders = [f"{key} = ?" for key in keys]
        search_by_placeholders=  [f"{key} = ?" for key in identifier_dict.keys()]
        command = f"""
            UPDATE {self.table_name} SET
            {' ,'.join(placeholders)}
            WHERE {'AND'.join(search_by_placeholders)};
"""
        print("multi update is running with command:")
        print(command)
        #print("with vals:",vals)

        cursor,connector = self.get_connection()
        success = False
        try:
            cursor.execute(command,vals)
            connector.commit()
            success = True
        except Exception as e:
            print(f"multi update failed. because: {e}")
        finally:
            cursor.close()
            connector.close()

        return success


    def create_new_entry(self,newuser:dict,strict=True):
        """the data should be in a dict format we will simply match the cols to the ones in the database
        expects a dict where the keys are the col names
        """
        success = False
        if len(self.col_names) > len(newuser) and strict:
            raise BaseException("not enough data to add to database")


        colnames = []
        datalist = []

        for key,val in newuser.items():
            colnames.append(key)
            datalist.append(val)


        if not (all(i in self.col_names for i in colnames)):
            print("colnames:",colnames)
            print("self.colnames:",self.col_names)
            raise BaseException("some cols are incorrect")

        cursor,connector = self.get_connection()
        col_names = f"{', '.join(colnames)}"
        placeholders = ",".join(['?' for i in colnames])
        
        try:
            lineweexecute = f"""INSERT INTO {self.table_name} ({col_names}) VALUES ({placeholders})"""
            #print(lineweexecute,datalist)
            cursor.execute(lineweexecute, tuple(datalist))
            
            connector.commit()
            success = True
        except sqlite3.Error as e:
            print("Insertion failed!")
            #print(e)
            connector.rollback()
            cursor.close()
            success = False
        finally:
            cursor.close()
        
        return success

    def get_row_dict(self,datatuple):
        """do not use this directly its only used for turning row data into json """
        temp = {key:val for key,val in zip(self.col_names,datatuple)}
        return temp





    def delete(self,col_name,col_value):
        cursor,connector = self.get_connection()
        values = [col_value]
        thisiswhatweexecute = f"""DELETE FROM {self.table_name} WHERE {col_name} = ?;"""
        print("deleting with",thisiswhatweexecute)
        success = False
        try:
                
            cursor.execute(thisiswhatweexecute,values)
            connector.commit()
            success = True
        except Exception as e:
            print(f"Could not delete, col_name:{col_name} with val:{col_value} because of: ", e)
        cursor.close()
        return success


    def get_db_state(self,debug=False,pruned=False,remove=[],tojson=False,groupbycol="id"):
        """prints the database so you see what you have inside
        - tojson: returns the data in a dict format
        - debug: saves the data into a json file
        - groupbycol: default to use the id col when using degub with json
        - pruned with remove: if you set prune to true and give cols those will be excluded from the results
        """
        if debug and groupbycol not in self.col_names:
            raise BaseException(f"the col given [ {groupbycol} ] is not present as a col in this database:, give a valid col and try again")

        

        cursor,connector = self.get_connection()
        default_command = f"""
            SELECT * FROM {self.table_name}
        """
        excluded = ",".join([col for col in self.col_names if col not in remove])
        prunned_command = f"""
            SELECT {excluded} FROM {self.table_name}

"""

        if pruned:
            cursor.execute(prunned_command)
        else:
            cursor.execute(default_command)
        temp = cursor.fetchall()
        print("|".join(c for c in self.col_names if c not in remove))
        for data in temp:
            print(" | ".join(str(d) if d != None else "" for d in data))


        if debug:
            jsoned = {}
            for user in temp:
                f = self.get_row_dict(user)
                jsoned[f[groupbycol]] = f

            with open(f"{self.db_name}_{self.table_name}.json","w") as new_db_state:
                json.dump(jsoned,new_db_state,indent=4)

            if tojson:
                return jsoned

        cursor.close()
        connector.commit()
        if debug:
            return jsoned
        return temp
  

if __name__ == "__main__":
    new_db_table = dbModel(
            db_name = "example.db",
            table_name = "users",
            col_names=["username","salary"],
            col_type = ["TEXT","REAL"]
        )
    new_db_table.create_new_entry({
        "username":"steve",
        "salary":"940 Euros"
    })
    new_db_table.get_db_state()