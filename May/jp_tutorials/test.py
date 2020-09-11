# import justpy as jp

# def hello_world():
#     wp = jp.WebPage()
#     jp.Hello(a=wp)
#     return wp

# jp.justpy(hello_world)

# import justpy as jp

# def my_click(self, msg):
#     self.text = 'I was clicked!'

# def hello_world():
#     wp = jp.WebPage()
#     d = jp.Div(text='Hello world!')
#     d.on('click', my_click)
#     wp.add(d)
#     return wp

# jp.justpy(hello_world)


# import justpy as jp
# import pandas as pd

# wm = pd.read_csv('https://elimintz.github.io/women_majors.csv').round(2)
# wm_under_20 = wm[wm.loc[0, wm.loc[0] < 20].index]
# wm_under_20.insert(0, 'Year', wm['Year'])

# def grid_test():
#     wp = jp.WebPage()
#     wm.jp.ag_grid(a=wp)
#     wm_under_20.jp.ag_grid(a=wp)
#     return wp

# jp.justpy(grid_test)

import justpy as jp
import pandas as pd

wm_df = pd.read_csv('https://elimintz.github.io/women_majors.csv').round(2)

def grid_test():
    wp = jp.WebPage()
    grid = wm_df.jp.ag_grid(a=wp)
    grid.options.pagination = True
    grid.options.paginationAutoPageSize = True
    grid.options.columnDefs[0].cellClass = ['text-white', 'bg-blue-500', 'hover:bg-blue-200']
    for col_def in grid.options.columnDefs[1:]:
        col_def.cellClassRules = {
            'font-bold': 'x < 20',
            'bg-red-300': 'x < 20',
            'bg-yellow-300': 'x >= 20 && x < 50',
            'bg-green-300': 'x >= 50'
        }
    return wp

jp.justpy(grid_test)

