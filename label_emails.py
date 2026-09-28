from googleapiclient.errors import HttpError

def get_or_create_label(service, label_name):
    """
    Checks if a label exists in Gmail by its name.
    If it exists, returns its ID. If not, creates it and returns the new ID.
    """
    try:
        # Get list of all labels
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        # Check if the label already exists
        for label in labels:
            if label['name'].lower() == label_name.lower():
                return label['id']
                
        # If not, create it
        label_object = {
            'name': label_name,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show'
        }
        created_label = service.users().labels().create(userId='me', body=label_object).execute()
        print(f"Created new label: '{label_name}'")
        return created_label['id']
        
    except HttpError as error:
        print(f'An error occurred while getting/creating label: {error}')
        return None

def apply_labels_to_email(service, message_id, category):
    """
    Applies the 'processed' label and a category label to the given message ID.
    """
    print(f"Applying labels to message {message_id}...")
    
    label_names = ["processed", category.lower()]
    label_ids_to_add = []
    
    for name in label_names:
        label_id = get_or_create_label(service, name)
        if label_id:
            label_ids_to_add.append(label_id)
            
    if not label_ids_to_add:
        print("Failed to find or create labels to apply.")
        return
        
    try:
        # First, fetch the message to get its threadId
        msg = service.users().messages().get(userId='me', id=message_id, format='minimal').execute()
        thread_id = msg.get('threadId')
        
        # Apply the labels to the thread and remove it from the INBOX
        body = {
            'addLabelIds': label_ids_to_add,
            'removeLabelIds': ['INBOX']
        }
        if thread_id:
            service.users().threads().modify(userId='me', id=thread_id, body=body).execute()
        else:
            service.users().messages().modify(userId='me', id=message_id, body=body).execute()
            
        print(f"Successfully applied labels {label_names} and removed message from INBOX.")
    except HttpError as error:
        print(f'An error occurred while applying labels: {error}')

