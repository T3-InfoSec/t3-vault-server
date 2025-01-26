def init_events():
    # Import all event modules here
    from app.database.events import task_event
    from app.database.events import task_assignment_event
    print("Events initialized")