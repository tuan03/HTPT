###cuộn dọc
__def__width = 100
__def__height = 100
__def__temp = tk.Frame(root, width=__def__width, height=__def__height, bg="green", borderwidth=0, highlightthickness=0)
__def__temp.place(x=5,y=5)
__def__canvas_root = tk.Canvas(__def__temp, width=__def__width-20, height=__def__height, bg="white", borderwidth=0, highlightthickness=0)
__def__canvas_root.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
__def__scrollbar = tk.__def__scrollbar(temp, orient=tk.VERTICAL, command=__def__canvas_root.yview,width=10)
__def__scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
__def__canvas_root.config(yscrollcommand=__def__scrollbar.set)


__def__sub_canvas = tk.Canvas(__def__canvas_root, width=100, height=100, bg="black",borderwidth=0, highlightthickness=0)
__def__canvas_root.create_window((0, 0), window=__def__sub_canvas, anchor=tk.NW)
__def__sub_canvas.update_idletasks()
__def__canvas_root.config(scrollregion=__def__canvas_root.bbox("all"))
update___def__scrollbar_visibility(__def__canvas_root,__def__scrollbar,__def__temp)
########