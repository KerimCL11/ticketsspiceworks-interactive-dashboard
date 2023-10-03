import pandas as pd
import streamlit as st

# Funciones auxiliares
def load_data(uploaded_file):
    data = pd.read_json(uploaded_file)
    return data

def process_data(data):
    ticket_entries = [entry for entry in data["tickets"]]
    ticket_df = pd.DataFrame(ticket_entries)
    
    user_entries = [user for user in data["users"] if user["role"] == "admin"]
    user_df = pd.DataFrame(user_entries)

    ticket_df = ticket_df.merge(user_df[['import_id', 'first_name', 'last_name']], left_on='assigned_to', right_on='import_id', how='left')
    ticket_df['assigned_name'] = ticket_df['first_name'] + " " + ticket_df['last_name']
    ticket_df["created_at_date"] = pd.to_datetime(ticket_df["created_at"]).dt.date
    
    return ticket_df

def apply_filters(ticket_df):
    st.sidebar.header("Filtros")
    
    selected_status = st.sidebar.multiselect("Seleccionar estado", ticket_df["status"].unique())
    selected_priority = st.sidebar.multiselect("Seleccionar prioridad", ticket_df["priority"].unique())
    selected_category = st.sidebar.multiselect("Seleccionar categoría", ticket_df["category"].unique())
    selected_assignee = st.sidebar.multiselect("Seleccionar persona asignada", ticket_df["assigned_name"].dropna().unique())
    
    filtered_tickets = ticket_df.copy()
    
    if selected_status:
        filtered_tickets = filtered_tickets[filtered_tickets["status"].isin(selected_status)]
    if selected_priority:
        filtered_tickets = filtered_tickets[filtered_tickets["priority"].isin(selected_priority)]
    if selected_category:
        filtered_tickets = filtered_tickets[filtered_tickets["category"].isin(selected_category)]
    if selected_assignee:
        filtered_tickets = filtered_tickets[filtered_tickets["assigned_name"].isin(selected_assignee)]
    
    search_term = st.text_input("Buscar ticket")
    if search_term:
        filtered_tickets = filtered_tickets[filtered_tickets["summary"].str.contains(search_term, case=False) |
                                            filtered_tickets["description"].str.contains(search_term, case=False)]
    
    return filtered_tickets

def display_charts(filtered_tickets):
    st.header("Distribución de Tickets por Estado")
    st.bar_chart(filtered_tickets["status"].value_counts())
    status_counts_df = filtered_tickets["status"].value_counts().reset_index()
    status_counts_df.columns = ['Estado', 'Count']
    st.table(status_counts_df)

    st.header("Distribución de Tickets por Categoría")
    st.bar_chart(filtered_tickets["category"].value_counts())
    category_counts_df = filtered_tickets["category"].value_counts().reset_index()
    category_counts_df.columns = ['Categoría', 'Count']
    st.table(category_counts_df)

    st.header("Cantidad y Porcentaje de Tickets por Categoría")
    category_counts = filtered_tickets["category"].value_counts()
    category_percentage = filtered_tickets["category"].value_counts(normalize=True) * 100
    category_table = pd.concat([category_counts, category_percentage], axis=1)
    category_table.columns = ["Cantidad", "Porcentaje (%)"]
    st.table(category_table)

    st.header("Distribución de Tickets por Persona Asignada")
    st.bar_chart(filtered_tickets["assigned_name"].value_counts())
    assigned_counts_df = filtered_tickets["assigned_name"].value_counts().reset_index()
    assigned_counts_df.columns = ['Persona Asignada', 'Count']
    st.table(assigned_counts_df)

def display_ticket_trend(ticket_df):
    st.header("Tendencia de Creación de Tickets")
    
    # Tendencia Diaria
    st.subheader("Tendencia Diaria")
    
    # Seleccionar fechas para tendencia diaria
    start_date = st.date_input("Fecha de inicio", ticket_df["created_at_date"].min())
    end_date = st.date_input("Fecha de finalización", ticket_df["created_at_date"].max())
    mask = (ticket_df["created_at_date"] >= start_date) & (ticket_df["created_at_date"] <= end_date)
    filtered_tickets = ticket_df.loc[mask]
    
    daily_data = filtered_tickets.groupby(pd.to_datetime(filtered_tickets["created_at_date"])).size()
    st.line_chart(daily_data)
    
    # Tendencia Mensual
    st.subheader("Tendencia Mensual")
    ticket_df['month_year'] = pd.to_datetime(ticket_df['created_at_date']).dt.to_period('M').astype(str)
    monthly_data = ticket_df.groupby('month_year').size().sort_values()
    st.line_chart(monthly_data)

    # Tabla de tickets creados por mes
    st.subheader("Tickets creados por mes")
    monthly_table = monthly_data.reset_index()
    monthly_table.columns = ['Mes y Año', 'Cantidad']
    monthly_table = monthly_table.sort_values(by="Mes y Año")
    monthly_table.loc[len(monthly_table)] = ["Total", monthly_table["Cantidad"].sum()]
    st.table(monthly_table)

def main():
    st.set_page_config(layout="wide")
    st.title("Dashboard de Tickets")
    
    uploaded_file = st.file_uploader("Por favor sube el archivo de tickets en formato JSON", type=["json"])
    
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        ticket_df = process_data(data)
        
        choice = st.sidebar.radio("Selecciona una opción", ["Dashboard", "Tendencia de Creación de Tickets"])
        if choice == "Dashboard":
            filtered_tickets = apply_filters(ticket_df)
            st.write(filtered_tickets)
            display_charts(filtered_tickets)
        elif choice == "Tendencia de Creación de Tickets":
            display_ticket_trend(ticket_df)
    else:
        st.write("Esperando el archivo JSON...")

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
