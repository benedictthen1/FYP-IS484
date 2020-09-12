import justpy as jp
import pandas as pd

grid_options = """
{
     defaultColDef: {
        flex: 1,
        minWidth: 20,
        filter: true,
        sortable: true,
        resizable: true,
        filterParams: {
        'buttons': ['reset', 'apply']
        },
    }, 
    enableRangeSelection: true,
    floatingFilter: true,
    
    pivotMode: false,
    sideBar: true,
    enableCharts: true
}
"""

ag_chart_options = """
{   
    autoSize: true,
    title: {
        text: 'Religions of London Population (2016)',
        fontSize: 18,
    },
    subtitle: {
        text: 'Source: Office for National Statistics',
    },
    series: [
        {
        data: [
            { religion: 'Christian', population: 4159000 },
            { religion: 'Buddhist', population: 97000 },
            { religion: 'Hindu', population: 456000 }
            ],
        type: 'pie',
        labelKey: 'religion',
        angleKey: 'population',
        label: {
            minAngle: 0,
        },
        callout: {
            strokeWidth: 2,
        },
        fills: [
            '#febe76',
            '#ff7979',
            '#badc58',
        ],
        strokes: [
            '#b28553',
            '#b35555',
            '#829a3e',
        ],
        },
    ],
    legend: {
        enabled: false,
    },
}
"""

high_chart_options = """
{
        chart: {
            type: 'bar'
        },
        title: {
            text: 'Fruit Consumption'
        },
        xAxis: {
            categories: ['Apples', 'Bananas', 'Oranges']
        },
        yAxis: {
            title: {
                text: 'Fruit eaten'
            }
        },
        series: [{
            name: 'Jane',
            data: [1, 0, 4]
        }, {
            name: 'John',
            data: [5, 7, 3]
        }]
}
"""

high_chart_options_2 = """
{
chart: {
        type: 'bar'
    },
    title: {
        text: 'Population pyramid for Germany, 2018'
    },
    subtitle: {
        text: 'Source: <a href="http://populationpyramid.net/germany/2018/">Population Pyramids of the World from 1950 to 2100</a>'
    },
    accessibility: {
        point: {
            valueDescriptionFormat: '{index}. Age {xDescription}, {value}%.'
        }
    },
    xAxis: [{
        categories: [
            '0-4', '5-9', '10-14', '15-19',
            '20-24', '25-29', '30-34', '35-39', '40-44',
            '45-49', '50-54', '55-59', '60-64', '65-69',
            '70-74', '75-79', '80-84', '85-89', '90-94',
            '95-99', '100 + '
        ],
        reversed: false,
        labels: {
            step: 1
        },
        accessibility: {
            description: 'Age (male)'
        }
    }, { // mirror axis on right side
        opposite: true,
        reversed: false,
        categories: [
            '0-4', '5-9', '10-14', '15-19',
            '20-24', '25-29', '30-34', '35-39', '40-44',
            '45-49', '50-54', '55-59', '60-64', '65-69',
            '70-74', '75-79', '80-84', '85-89', '90-94',
            '95-99', '100 + '
        ],
        linkedTo: 0,
        labels: {
            step: 1
        },
        accessibility: {
            description: 'Age (female)'
        }
    }],
    yAxis: {
        title: {
            text: null
        },
        accessibility: {
            description: 'Percentage population',
            rangeDescription: 'Range: 0 to 5%'
        }
    },

    labels: {
      formatter: '{value}'
    },

    plotOptions: {
        series: {
            stacking: 'normal'
        }
    },

    series: [{
        name: 'Male',
        data: [
            -2.2, -2.1, -2.2, -2.4,
            -2.7, -3.0, -3.3, -3.2,
            -2.9, -3.5, -4.4, -4.1,
            -3.4, -2.7, -2.3, -2.2,
            -1.6, -0.6, -0.3, -0.0,
            -0.0
        ]
    }, {
        name: 'Female',
        data: [
            2.1, 2.0, 2.1, 2.3, 2.6,
            2.9, 3.2, 3.1, 2.9, 3.4,
            4.3, 4.0, 3.5, 2.9, 2.5,
            2.7, 2.2, 1.1, 0.6, 0.2,
            0.0
        ]
    }]
}
"""

citi_df = pd.read_csv('../TestData.csv')

def grid_test():
    wp = jp.WebPage()
    grid = citi_df.jp.ag_grid(a=wp, options=grid_options)
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
    #chart = jp.AgGrid(a=wp, options=ag_chart_options)
    high_chart = jp.HighCharts(a=wp,options=high_chart_options, classes='m-2 p-2 border', style='width: 600px')
    high_chart_2 = jp.HighCharts(a=wp,options=high_chart_options_2, classes='m-2 p-2 border', style='width: 600px')
    return wp

jp.justpy(grid_test)