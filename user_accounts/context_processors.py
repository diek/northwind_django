"""
Key characteristics and uses of Django context processors:
Global Data Availability: Context processors are designed to provide data that
needs to be accessible across multiple templates, such as site-wide settings,
user information, navigation links, or dynamically generated content like a
list of categories.

Function Signature: A context processor is a function that takes a single
argument, the HttpRequest object, and returns a dictionary. The keys of
this dictionary become variable names in the template context, and
their corresponding values are the data accessible in the templates.

Avoiding Code Duplication: By centralizing the logic for common data, context
processors help reduce code repetition in your views and improve the
maintainability of your application.

Built-in Processors: Django includes several built-in context processors for
common functionalities, such as auth (for user information), messages (for
Django messages framework), request (for accessing the request object), and
debug (for debugging information).
"""


def my_context_processor(request):
    return {
        "site_name": "Django and Northwind",
        "current_year": 2025,
    }
