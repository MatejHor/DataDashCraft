import re
import dash
import dash_bootstrap_components as dbc
from dash import html, callback_context
from dash.dependencies import Input, Output, State

import helpers.functions as hf
import helpers.storage as st

# Define the Dash APP 
external_stylesheets = [dbc.themes.DARKLY]  # BOOTSTRAP
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Database UI"
data_models = hf.get_models()

# Define the app layout with Bootstrap components
app.layout = dbc.Container(
    [
        html.Link(rel="stylesheet", href="./boostrap_style.css"),
        html.H1("Database UI", className="text-center my-3 back"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.DropdownMenu(
                            label="Tables",
                            id="dd-tables-name",
                            direction="down",
                            color="primary",
                            children=[
                                dbc.DropdownMenuItem("Project", id="dd-Project"),
                                # dbc.DropdownMenuItem("<another-model>", id="dd-<AnotherModel>"),
                            ],
                        )
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            "Refresh",
                            id="btn-refresh",
                            color="info",
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        dbc.DropdownMenu(
                            label="Add item",
                            id="dd-add",
                            direction="down",
                            color="primary",
                            children=[
                                dbc.DropdownMenuItem(
                                    header=True,
                                    children=dbc.Button(
                                        "Add Item",
                                        id="btn-add",
                                        color="primary",
                                    ),
                                )
                            ],
                        ),
                    ],
                    width="auto",
                ),
                dbc.Col(
                    [
                        dbc.DropdownMenu(
                            label="Hidden columns",
                            direction="down",
                            color="info",
                            children=[
                                dbc.DropdownMenuItem(
                                    header=True,
                                    children=[
                                        dbc.Checklist(
                                            id="cl-hidden-column",
                                            options=[],
                                            value=[],
                                        )
                                    ],
                                )
                            ],
                        ),
                    ],
                    width="auto",
                ),
                dbc.Button(
                    id="btn-open-delete",
                    color="info",
                    style={"display": "none"},
                ),
            ]
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Delete item", id="m-delete-header")),
                dbc.ModalBody("", id="m-delete-label"),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            "Confirm",
                            id="btn-confirm-delete",
                            color="danger",
                            n_clicks=None,
                        )
                    ]
                ),
            ],
            id="m-delete-window",
            size="lg",
            is_open=False,
        ),
        html.Hr(),
        html.Div(
            id="projects-table",
            children=[
                dash.dash_table.DataTable(id="data-table")
            ],
            className="table-dark",
        ),
        html.Br(),
    ],
    fluid=True,
    className="dbc",
)


@app.callback(
    Output("dd-tables-name", "label"),
    Input("dd-Project", "n_clicks"),
    # Input("dd-<another-model>", "n_clicks"),
    State("dd-tables-name", "label"),
    prevent_initial_update=True,
)
def set_datatable_name(datatable_l1, datatable_name):
    ctx = callback_context
    if ctx.triggered:
        datatable_name = ctx.triggered[0]["prop_id"]
        datatable_name = datatable_name.split(".")[0]
        datatable_name = datatable_name.split("-")[1]
    return datatable_name


@app.callback(
    Output("projects-table", "children"),
    Output("cl-hidden-column", "options"),
    Output("cl-hidden-column", "value"),
    Output("dd-add", "children"),
    Input("btn-refresh", "n_clicks"),
    State("dd-tables-name", "label"),
    prevent_initial_update=True,
)
def load_datatable(refresh_btn, datatable_name):
    # IF RESFRESH/LOAD was triggered
    if callback_context.triggered and datatable_name in data_models:
        # Import model
        db_model = hf.import_data_model(datatable_name)
        with st.SESSION() as session:
            data = [item.to_dict() for item in db_model.get_list(session)]
        # Get columns names
        columns = db_model.get_columns()
        # Names of columns for hide column checklist
        hide_columns_checklist = [{"label": column, "value": column} for column in columns]
        # Hide all ids
        hidden_columns = list(filter(lambda x: db_model.get_primary_key() == x, columns))

        # Add inputs and labels  for add-dropdown
        add_button_children = []
        for column in columns:
            if column != db_model.get_primary_key():
                add_button_children.append(hf.get_input_add(column))
        add_button_children.append(hf.get_button_add(False))

        return (
            dash.dash_table.DataTable(
                id="data-table",
                columns=[{"name": i, "id": i, "hideable": True} for i in columns],
                hidden_columns=hidden_columns,
                data=data,
                editable=True,
                row_deletable=True,
                filter_action="native",
                sort_action="native",
                style_table={"overflowX": "auto"},
                css=[{"selector": ".show-hide", "rule": "display: none"}], # hide original toggle hide button
            ),
            hide_columns_checklist,
            hidden_columns,
            add_button_children,
        )

    return (
        dash.dash_table.DataTable(id="data-table"),
        [],
        [],
        [hf.get_button_add(True)],
    )


@app.callback(
    Output("btn-refresh", "n_clicks"),
    Output("btn-add", "n_clicks"),
    Input("btn-add", "n_clicks"),
    State("dd-add", "children"),
    State("dd-tables-name", "label"),
    prevent_initial_update=True,
)
def add_datatable_item(add_btn, add_inputs, datatable_name):
    if add_btn is None or add_btn == 0:
        return 0, 0
    else:
        new_item = {}
        for input in add_inputs:
            item = input["props"]
            if "children" in item and type(item["children"]) == list:
                column_value = item["children"][1]["props"]["value"]
                if column_value.isnumeric():
                    column_value = int(column_value)
                column_name = re.sub("add-column-", "", item["children"][1]["props"]["id"])
                new_item[column_name] = column_value

        db_model = hf.import_data_model(datatable_name)
        with st.SESSION() as session:
            new_item = db_model(**new_item)
            db_model.add(session, new_item)
        return 1, 0


@app.callback(
    Output("data-table", "hidden_columns"), 
    Input("cl-hidden-column", "value")
)
def hide_datatable_column(checklist):
    return checklist


@app.callback(
    Output("m-delete-window", "is_open"),
    Input("btn-confirm-delete", "n_clicks"),
    Input("btn-open-delete", "n_clicks"),
    State("dd-tables-name", "label"),
    State("m-delete-label", "children"),
    State("m-delete-window", "is_open"),
)
def delete_datatable_item(confirm_btn, open_btn, datatable_name, delete_label, is_open):
    ctx = callback_context
    if (
        ctx.triggered
        and "onfirm" in ctx.triggered[0]["prop_id"]
        and ctx.triggered[0]["value"]
    ):
        with st.SESSION() as session:
            db_model = hf.import_data_model(datatable_name)
            id = delete_label.split("id=")[1]
            db_model.delete_by_id(session, id)
        return False
    elif (
        ctx.triggered
        and "open" in ctx.triggered[0]["prop_id"]
        and ctx.triggered[0]["value"]
    ):
        return True
    return is_open


@app.callback(
    Output("btn-open-delete", "n_clicks"),
    Output("m-delete-label", "children"),
    Input("data-table", "data"),
    State("data-table", "data_previous"),
    State("dd-tables-name", "label"),
)
def update_datatable_item(current_datatable, previous_datatable, datatable_name):
    if previous_datatable is None:
        return None, ""
    # Import 
    db_model = hf.import_data_model(datatable_name)
    pk_name = db_model.get_primary_key()

    previous_datatable_key = [item[pk_name] for item in previous_datatable]
    current_datatable_key = [item[pk_name] for item in current_datatable]

    with st.SESSION() as session:
        # Handling delete
        if previous_datatable_key != current_datatable_key:
            for index, key in enumerate(previous_datatable_key):
                if key not in current_datatable_key:
                    return (
                        1,
                        f"Confirm to remove item with id={previous_datatable[index][pk_name]}",
                    )
        else:
            # UPDATE
            for previous_item, current_item in zip(previous_datatable, current_datatable):
                if previous_item != current_item:
                    updated_item = db_model.get(session, current_item[pk_name])
                    db_model.update(session, updated_item, current_item)
                    return None, ""

    return None, ""


# Initialize the app
if __name__ == "__main__":
    app.run_server(debug=True)
