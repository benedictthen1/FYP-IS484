import React, {Component} from 'react';
import PropTypes from 'prop-types';
import { AgGridReact } from 'ag-grid-react';

import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-alpine.css';

/**
 * Dashcustomgrid is a component wrapped on ag-Grid.
 * It takes two property, `columnDefs`, and `rowData`
 * displays them.
 */
export default class Dashcustomgrid extends Component {

    onSelectionChanged () {
        var selectedRows = this.props.gridApi.getSelectedRows();
        this.props.setProps({selectedRows: selectedRows});
    }

    render() {
        const {id, columnDefs, setProps, rowData} = this.props;

        return (
            <div id={id}>
                <div> An ag-Grid Component in Dash </div>
                <div className="ag-theme-alpine" style={ {height: '300px', width: '800px'} }>
                    <AgGridReact
                        onGridReady={(params) => {
                            setProps({gridApi:params.api, isGridReady:true})
                        }}
                        rowSelection='single' 
                        onSelectionChanged={this.onSelectionChanged.bind(this)}
                        columnDefs={columnDefs}
                        rowData={rowData}>
                    </AgGridReact>
                </div>
            </div>
        );
    }
}

Dashcustomgrid.defaultProps = {};

Dashcustomgrid.propTypes = {
    /**
     * The ID used to identify this component in Dash callbacks.
     */
    id: PropTypes.string,
    /**
     *gridApi for ag-Grid.
     */
    gridApi: PropTypes.object,
    /**
     *columnDefs for ag-Grid.
     */
    columnDefs: PropTypes.array,

    /**
     * rowData for ag-Grid.
     */
    rowData: PropTypes.array,

    /**
     * selectedRows for ag-Grid.
     */
    selectedRows: PropTypes.array,
    /**
     * Dash-assigned callback that should be called to report property changes
     * to Dash, to make them available for callbacks.
     */
    setProps: PropTypes.func
};