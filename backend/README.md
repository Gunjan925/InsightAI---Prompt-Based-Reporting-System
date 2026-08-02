Endpoint	Method	Description
/api/auth/register	POST	Registers a new user with a unique username, email, and password.
/api/auth/login	POST	Authenticates the user and returns a JWT access token.
/api/auth/me	GET	Retrieves the profile details of the currently authenticated user.
/api/auth/logout	POST	Logs out the current user (frontend removes the stored JWT token).
/api/upload	POST	Uploads a CSV or Excel dataset after validating its type and size, then stores it in MySQL.
/api/report	POST	Generates an AI-powered report for an uploaded dataset using the provided prompt.
/api/report/{report_id}	GET	Retrieves the complete generated report for the specified report ID.
/api/report/{report_id}/download	GET	Downloads the generated report as an interactive HTML document.
/api/history	GET	Returns the authenticated user's previously generated reports in reverse chronological order.
/api/dashboard	GET	Returns dashboard statistics such as uploaded files, generated reports, latest report, and file type distribution.