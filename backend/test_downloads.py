from app.services.npm_monitor import get_downloads

downloads = get_downloads("express")

print("Express downloads last week:", downloads)
