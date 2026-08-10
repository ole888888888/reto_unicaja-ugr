import datetime
from typing import Any

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from src.services.charts import eChartInfo, get_echart_config, seriesInfo
from src.services.client import read_client_info
from src.services.contact import (
    add_contact_logic,
    delete_contact_logic,
    get_contacts_logic,
)
from src.services.faq import get_faq_answer
from src.services.transactions import (
    make_transfer,
    read_transactions_info,
)

#In this file we can find the tools which the llm has access to, the logic is separated in the services folder.

@tool
def read_client_information(config: RunnableConfig) -> str:
    """
    Retrieve profile information for the currently authenticated user.

    Use this tool whenever you need details about the logged-in user, either
    because they explicitly asked for it or because it is required to answer a query.
    
    The retrieved details include the user's ID, full name, email address,
    current account balance, phone number, and city.

    Args:
        config (RunnableConfig): Runtime configuration containing context metadata,
            such as the authenticated user ID.

    Returns:
        str: A string with the user's profile information or an error message should the information not be found.
    """
    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Unauthenticated client, can't proceed."

    return read_client_info(client_id)

@tool
def get_current_date_and_time():
    """
    Retrieve the current date and time in UTC formatted as an ISO 8601 string.

    Use this tool whenever you need to know the present date, time, or year,
    especially for calculating relative dates (e.g., 'today', 'yesterday',
    'this month', or checking recent transactions).

    Returns:
        str: The current UTC timestamp in ISO 8601 format (e.g., '2026-07-24T19:23:49+00:00').
    """
    return datetime.datetime.now(tz=datetime.UTC).isoformat()
    
@tool
def read_transactions_information( config: RunnableConfig,
                                start_date: str|None = None,
                                end_date: str|None = None, 
                                min_amount: float|None = None, 
                                max_amount: float|None = None, 
                                category:str|None = None
                                ) -> str:
    """
    Retrieve and filter transaction history for the currently authenticated user.

    Use this tool whenever the user asks about their past spending, income, or transaction
    history. You can apply filters by date range, transaction amount (in Euros €),
    or category.

    Present the data calling the create_table tool. Do NOT generate introductory text,
    concluding text or Markdown tables, simply call the create_tool call.

    Args:
        config (RunnableConfig): Runtime configuration containing context metadata, 
            such as the authenticated user ID.
        start_date (str | None, optional): Start date for filtering in 'YYYY-MM-DD' format.
            Defaults to None.
        end_date (str | None, optional): End date for filtering in 'YYYY-MM-DD' format.
            Defaults to None.
        min_amount (float | None, optional): Minimum transaction amount in Euros (€).
            Defaults to None.
        max_amount (float | None, optional): Maximum transaction amount in Euros (€).
            Defaults to None.
        category (str | None, optional): Category name to filter transactions
            (e.g., 'supermarket', 'restaurants', 'transfers'). Defaults to None.

    Returns:
        str: A string listing the matching transactions or an error message if the
            user is not authenticated.
    """

    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Unauthenticated client, can't proceed."

    return read_transactions_info(client_id,start_date,end_date,min_amount,max_amount,category)

@tool
def make_transfer_tool(config: RunnableConfig, amount: float, concepto: str, tel: str) -> str:
    """
    Execute a money transfer or Bizum to a saved contact using their phone number.

    Use this tool whenever the user asks to send money, make a transfer, or send a 'Bizum'
    to a recipient using their phone number. The recipient must be in the user's contacts.

    Args:
        config (RunnableConfig): Runtime configuration containing context metadata, such as the authenticated user ID.
        amount (float): The amount of money to transfer in Euros (€). Must be greater than 0.
        concepto (str): The description, concept, or note for the transfer.
        tel (str): The recipient's phone number in E.164 format (e.g., '+34612345678').

    Returns:
        str: A string indicating whether the transfer was successful (including the updated balance)
            or an error message if the transaction failed.
    """

    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Unautheticated client, can't proceed."
    
    return make_transfer (client_id,amount,concepto,tel)


@tool
def get_bank_faqs(query: str) -> str:
    """
    Searches the bank's official Frequently Asked Questions (FAQ) database.

    Use this tool whenever the user asks specific questions about bank services,
    products, accounts, fees, or operational procedures to retrieve official answers.

    Args:
        query (str): The user's question or topic keywords to search in the FAQ database.

    Returns:
        str: Relevant official FAQ matching information or a not-found message.
    """
    return get_faq_answer(query)

@tool 
def get_contacts (config: RunnableConfig, name: str|None = None) -> str:
    """
    Retrieves saved contacts (names and phone numbers) for the authenticated user.

    Use this tool when the user asks for their contact list, or needs to find a 
    specific contact's phone number (e.g., before making a transfer or sending a message).

    Args:
        name (str | None, optional): Name or keyword to filter a specific contact. 
            Pass `None` or leave empty to retrieve all contacts. Defaults to None.

    Returns:
        str: A JSON string array with matching contact details `[{"nombre": ..., "tel": ...}]`,
            or an error/not-found message.
    """
        
    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Unauthenticated client, can't procede."

    return get_contacts_logic(client_id, name)

@tool
def add_contact (config: RunnableConfig, tel: str, name: str|None = None) -> str:
    """
    Adds a new contact for the authenticated user.

    Use this tool when the user wants to save or store a contact. 
    Requires a mandatory phone number, while the contact name is optional.

    Args:
        tel (str): The contact's phone number (mandatory).
        name (str | None): The name associated with the contact (optional).

    Returns:
        str: A status message confirming whether the contact was created 
            or if authentication failed.
    """

    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Cliente no autentificado, no se puede continuar."

    return add_contact_logic(client_id, tel, name)

@tool 
def delete_contact (config: RunnableConfig, tel: str) -> str:
    """
    Deletes a contact associated with the authenticated user using their phone number.

    Use this tool to remove a contact from the database. A valid phone number is 
    strictly required to perform the deletion. If the user only provides a name, 
    search for their contact details first to retrieve the phone number, before calling this tool.

    Args:
        tel (str): The phone number of the contact to delete (required).

    Returns:
        str: A confirmation message indicating the result of the deletion 
        or an error message if unauthenticated.
    """
    client_id = config.get("configurable", {}).get("user_id")

    if not client_id:
        return "Cliente no autentificado, no se puede continuar"
    
    return delete_contact_logic(client_id,tel)

@tool (args_schema=eChartInfo)
def create_chart (        
    series: list[seriesInfo],
    title: str|None = None,
    x_axis_categories: list[str]|None = None
    ) -> dict[str, Any]:
    """
    Generates an ECharts JSON configuration option dictionary for frontend rendering.

    CRITICAL INSTRUCTION FOR CHARTS:
    When the user asks for a chart or data visualization, you MUST call the `create_chart` tool.
    Do NOT generate any introductory text, concluding text, descriptions, explanations, or Markdown image links before or after calling the tool. 
    Your turn must consist ONLY of the `create_chart` tool call. 
    DO NOT include Markdown image syntax, attachments, or image links (e.g., do not output `![...](attachment://...)`) in your text response.

    Args:
        series (list[seriesInfo]): Data series containing the chart type, series name,
            and data points.
        title (str | None, optional): Main title displayed on the chart. Defaults to None.
        x_axis_categories (list[str] | None, optional): Category labels for the x-axis.
            Defaults to None.

    Returns:
        dict[str, Any]: The raw ECharts option dictionary to be consumed by the frontend.
    """
    return get_echart_config (series=series, title=title, x_axis_categories=x_axis_categories)

@tool
def create_table (
    data: list[dict[str, Any]],
    ) -> list[dict[str,Any]]:
    """
    Generates a structured table view for the user. Use this tool whenever presenting 
    tabular data like transaction histories, user lists, or search results.

    Args:
        data: A list of key-value dictionaries representing table rows. 
              Keys are column headers, values are cell entries.
              Example: [{"Date": "2026-08-01", "Concept": "Supermarket", "Amount": "45.00 €"}]
    """
    return data

tools = [
    read_client_information,
    get_current_date_and_time,
    read_transactions_information,
    make_transfer_tool,
    get_bank_faqs,
    get_contacts,
    delete_contact,
    add_contact,
    create_chart,
    create_table,
]
