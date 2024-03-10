import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import pandas as pd
import sqlite3
from tkinter import filedialog, messagebox

class myTreeView(ttk.Treeview):
    def __init__(self, master, df, **kwargs):
        super().__init__(master, **kwargs)
        self.df = df
        self.row_identifier_to_index = []
        self.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):

        region_clicked = self.identify("region", event.x, event.y)
        # print(f'You clicked on {region_clicked}')
        if region_clicked == "cell":
            column = self.identify_column(event.x)
            print(f'You clicked on column {column}')   
            column_index = int(column.replace('#', ''))         
            item = self.identify("item", event.x, event.y)
            print(f'You clicked on item {item}')
            selected_item = self.item(item, "values")[column_index-1]
            print(f'You selected {selected_item}')
            
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
        self.row_identifier_to_index = self.df.index.tolist()
        print(self.row_identifier_to_index)
        entry = event.widget
        new_value = entry.get()
        column = entry.editing_column_index - 1
        item = entry.editing_item
        self.set(item, column, new_value)
        
        # Update the dataframe
        row_index = self.row_identifier_to_index[int(item)]
        column_name = self.heading(column)["text"].lower()
        # print(f'Row index: {row_index}, Column name: {column_name}, New value: {new_value}')
        # print(self.df)
        self.df.at[row_index, column_name] = new_value  # Update value in the DataFrame
        entry.destroy()
        # print(self.df)
    
    def load_file(self, file_path):
        try:
            if file_path.endswith('.csv'):
                self.df = pd.read_csv(file_path)
                self.refresh_treeview()
            elif file_path.endswith('.txt'):
                self.df = pd.read_csv(file_path, delimiter='\t')
                self.refresh_treeview()
            elif file_path.endswith('.xlsx'):
                self.df = pd.read_excel(file_path)
                self.refresh_treeview()
        except Exception as e:
            print(f"Error loading file: {e}")

    def refresh_treeview(self):
        self.delete(*self.get_children())
        self['columns'] = list(self.df.columns)
        self['show'] = 'headings'
        for col in self.df.columns:
            self.heading(col, text=col.capitalize())
            self.column(col, anchor="center")
        for row in self.df.itertuples():
            self.insert('', 'end', values=row[1:], iid=row[0])

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

def search_name(event=None):
    search_query = search_entry.get().strip().upper()
    if search_query:
        tree.delete(*tree.get_children())  # Clear the treeview
        for row in db.itertuples():
            if search_query in row.name:
                tree.insert('', 'end', values=row[1:], iid=row[0])
    else:
        tree.delete(*tree.get_children())
        for row in db.itertuples():
            tree.insert('', 'end', values=row[1:], iid=row[0])
    search_entry.delete(0, 'end')  # Clear the search entry

def load():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", ["*.csv", "*.txt"]), ("Excel files", "*.xlsx"), ("All Files", "*.*")])
    if file_path:
        display_button.configure(state="normal")
        display_tree.load_file(file_path)

def display_date():
    if display_tree.df.empty:
        messagebox.showinfo("Error", "No file loaded")
    else:
        try:
            display_tree.df = pd.merge(display_tree.df, db, on='name', how='left')
            display_tree.refresh_treeview()
            display_button.configure(state="disabled")
        except KeyError:
            print("Error: 'name' column not found in one of the DataFrames.")
        except Exception as e:
            print(f"Error merging DataFrames: {e}")

def export_data():
    if not display_tree.df.empty:
        filename = filedialog.asksaveasfilename(filetypes=[("Text files", "*.csv")], defaultextension=".csv")
        if filename:
            try:
                display_tree.df.to_csv(filename, index=False)
            except Exception as e:
                print(f"Error exporting data: {e}")
    else:
        print("No data to export")

def insert_row():
    if not display_tree.df.empty:
        columns = [display_tree.df.columns]  # Example data
        for col in columns:
            data = dict.fromkeys(col, 'None')
        # print(data)
        
        new_row=pd.DataFrame([data])
        display_tree.df = pd.concat([display_tree.df, new_row], ignore_index=True)
        # print(display_tree.df)
        display_tree.refresh_treeview()

def delete_row():
    if not display_tree.df.empty:
        row_identifier_to_index = display_tree.df.index.tolist()
        selected_item = display_tree.selection()[0]
        # print(f'selected item {selected_item}')
        display_tree.delete(selected_item)
        
        # Update the dataframe
        display_tree.df = display_tree.df.drop(row_identifier_to_index[int(selected_item)]).reset_index(drop=True)
        # print(display_tree.df)
        display_tree.refresh_treeview()

if __name__ == '__main__':
    
    root = ctk.CTk()
    root.title('Etiquette Tool')
    root.grid_rowconfigure(0, weight=1)  
    root.grid_columnconfigure(0, weight=1)

    # Tab view
    tab_view = ctk.CTkTabview(root, anchor='w')
    tab_1 = 'Search'
    tab_2 = 'Load File'
    tab_view.add(tab_1)
    tab_view.add(tab_2)
    tab_view.grid(row=0, column=0, sticky="nsew")
  
    tab_view.tab(tab_1).rowconfigure(1, weight=1)
    tab_view.tab(tab_1).columnconfigure(0, weight=1)

    tab_view.tab(tab_2).rowconfigure(1, weight=1)
    for i in range(5):
        tab_view.tab(tab_2).columnconfigure(i, weight=1)
    
    # Load the datset from database
    db = get_records()
    db.reset_index(inplace=True)
    
    # Tab1
    ## Create a search entry
    search_entry = ctk.CTkEntry(tab_view.tab(tab_1), placeholder_text="Search name")
    search_entry.grid(row=0, column=0, padx=10, pady=10)
    search_entry.bind("<Return>", search_name)

    ## Display the dataframe in a treeview
    tree = myTreeView(tab_view.tab(tab_1), df=db, columns=list(db.columns), show='headings')

    for col in db.columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, anchor="center")

    for row in db.itertuples():
        tree.insert('', 'end', values=row[1:], iid=row[0]) # row[0] is the index

    tree.grid(row=1, column=0, padx=10, sticky="nsew")
    
    ## Create a scrollbar
    scrollbar = ctk.CTkScrollbar(tab_view.tab(tab_1))
    scrollbar.grid(row=1, column=0, sticky="nse")
    scrollbar.configure(command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    # Tab2
    ## Frames
    file_frame = ctk.CTkFrame(tab_view.tab(tab_2), border_width=2, border_color="white")
    file_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="n")
    row_frame = ctk.CTkFrame(tab_view.tab(tab_2), border_width=2, border_color="white")
    row_frame.grid(row=0, column=3, columnspan=2, padx=10, pady=10, sticky="n")
    
    ## Buttons
    load_button = ctk.CTkButton(file_frame, text="Load", command=load)
    load_button.grid(row=0, column=0, padx=10, pady=10)

    display_button = ctk.CTkButton(file_frame, text="Display", command=display_date)
    display_button.grid(row=0, column=1, padx=10, pady=10)

    export_button = ctk.CTkButton(file_frame, text="Export", command=export_data)
    export_button.grid(row=0, column=2, padx=10, pady=10)

    insert_button = ctk.CTkButton(row_frame, text="Insert row", command=insert_row)
    insert_button.grid(row=0, column=3, padx=10, pady=10)

    delete_button = ctk.CTkButton(row_frame, text="Delete row", command=delete_row)
    delete_button.grid(row=0, column=4, padx=10, pady=10)

    ## Display the dataframe in a treeview
    placeholder_text = "No data loaded"
    display_tree = myTreeView(tab_view.tab(tab_2), df=pd.DataFrame(), columns=[placeholder_text], show='headings')
    display_tree.heading(placeholder_text, text=placeholder_text)
    display_tree.grid(row=1, column=0, columnspan=5, padx=10, sticky="nsew")

    ## Create a scrollbar
    scrollbar = ctk.CTkScrollbar(tab_view.tab(tab_2))
    scrollbar.grid(row=1, column=4, sticky="nse")
    scrollbar.configure(command=display_tree.yview)
    display_tree.configure(yscrollcommand=scrollbar.set)
    
    root.mainloop()
    