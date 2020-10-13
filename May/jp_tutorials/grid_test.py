# import justpy as jp

# grid_options = """
# {
    
#       columnDefs: [
#       {headerName: "Make", field: "make", filter: 'agSetColumnFilter'},
#       {headerName: "Model", field: "model", filter: 'agSetColumnFilter'},
#       {headerName: "Price", field: "price", filter: 'agNumberColumnFilter'}
#     ],
#       rowData: [
#       {make: "Toyota", model: "Celica", price: 35000},
#       {make: "Ford", model: "Mondeo", price: 32000},
#       {make: "Porsche", model: "Boxter", price: 72000}
#     ],
#     defaultColDef: {
#         flex: 1,
#         minWidth: 200,
#         resizable: true,
#         floatingFilter: true,
#     }, 
#     enableRangeSelection: true,
# }
# """

# def grid_test():
#     wp = jp.WebPage()
#     grid = jp.AgGrid(a=wp, options=grid_options)
#     return wp
# jp.justpy(grid_test)

import justpy as jp

grid_options = """
{
    defaultColDef: {
        filter: true,
        sortable: true,
        resizable: true,
        cellStyle: {textAlign: 'center'},
        headerClass: 'font-bold'
    }, 
      columnDefs: [
      {headerName: "Make", field: "make"},
      {headerName: "Model", field: "model"},
      {headerName: "Price", field: "price"},
      {headerName: "Enabled", field: "enabled", cellRenderer: 'checkboxRenderer'}
    ],
      rowData: [
      {make: "Toyota", model: "Celica", price: 35000, enabled: false},
      {make: "Ford", model: "Mondeo", price: 32000, enabled: true},
      {make: "Porsche", model: "Boxter", price: 72000, enabled: false}
    ]
}
"""


def grid_change(self, msg):
    print(msg)


def grid_test():
    wp = jp.WebPage()
    grid = jp.AgGrid(a=wp, options=grid_options)
    grid.on('cellValueChanged', grid_change)
    return wp


jp.justpy(grid_test)