import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import pandas as pd
import sqlite3

class myTreeView(ttk.Treeview):
    def __init__(self, master, df, **kwargs):
        super().__init__(master, **kwargs)
        self.df = df
        self.bind("<Double-1>", self.on_double_click)
    
    def on_double_click(self, event):

        region_clicked = self.identify("region", event.x, event.y)
        if region_clicked == "cell":
            column = self.identify_column(event.x)   
            column_index = int(column.replace('#', ''))         
            item = self.identify("item", event.x, event.y)
            selected_item = self.item(item, "values")[column_index-1]
            
            # Create an entry widget and place it in the cell selected
            box = self.bbox(item, column)
            entry = ttk.Entry(self, )
            ## Entry contains the selected item
            entry.editing_column_index = column_index
            entry.editing_item = item
            entry.insert(0, selected_item)
            entry.select_range(0, 'end')
            entry.focus()
            ## Loose focus when clicked outside the entry
            entry.bind("<FocusOut>", self.on_focus_out)
            ## Update the cell value when the user presses the enter key
            entry.bind("<Return>", self.on_enter_key)

            entry.place(x=box[0], y=box[1], width=box[2], height=box[3])
        else:
            print(f'You clicked on {region_clicked}')

    def on_focus_out(self, event):
        event.widget.destroy()
    
    def on_enter_key(self, event):
        entry = event.widget
        new_value = entry.get()
        column = entry.editing_column_index - 1
        item = entry.editing_item
        self.set(item, column, new_value)
        
        # Update the dataframe
        row_index = int(item[1:]) - 1  # Convert item ID to row index
        column_name = self.heading(column)["text"]
        # print(f'Row index: {row_index}, Column name: {column_name}, New value: {new_value}')
        # print(self.df)
        self.df.at[row_index, column_name.lower()] = new_value  # Update value in the DataFrame
        entry.destroy()
        print(self.df)

def get_records():
    conn = create_db_connection()
    if conn is not None:
        try:
            db = pd.read_sql_query('''SELECT name, '2024-'|| format('%02d',month)||'-'|| format('%02d',day) as date  
                    FROM Names JOIN Date ON Names.id = Date.name_id ''', 
                    conn, index_col='name')
            # db['date'] = pd.to_datetime(db['date'])
        except Exception as e:
            print(f'Error getting all data: {e}')
        finally:
            conn.close()
            return db   

def create_db_connection():
    try:
        conn = sqlite3.connect('celebration.db')
        return conn
    except sqlite3.Error as e:
        print(f'Error connecting to the database: {e}')
        return None


if __name__ == '__main__':
    
    root = ctk.CTk()
    
    db = get_records()
    db.reset_index(inplace=True)
    
    # Display the dataframe in a treeview
    tree = myTreeView(root, df=db, columns=list(db.columns), show='headings')

    for col in db.columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, anchor="center")

    for row in db.itertuples():
        tree.insert('', 'end', values=row[1:]) # row[0] is the index


    tree.pack()
    
    root.mainloop()
    