back for different Tab Content Layout. ###
# @app.callback(
#     [Output("tab_content", "children")],
#     [Input('client_asset_type_tabs', 'active_tab')]
# )
# def tab_content_layout(selected_tab):
#     excel_tabs = ["CASH & LIABILITIES","EQUITIES","FIXED INCOME","ALTERNATIVE INVESTMENTS","CAPITAL MARKETS"]
#     if selected_tab in excel_tabs:
#         print("It came into layout section!")
#         return standard_tab_content