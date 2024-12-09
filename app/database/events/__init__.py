def init_events():
    # Import all event modules here
    from app.database.events import task_event
    print("Events initialized")