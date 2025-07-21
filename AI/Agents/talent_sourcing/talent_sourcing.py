def getDetails(job_description: str):

    return [
        {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-123-456-7890",
            "job_role": "Senior Software Engineer"
        },
        {
            "name": "Jane Smith",
            "email": "jane.smith@example.com",
            "phone": "+1-987-654-3210",
            "job_role": "Backend Developer"
        },
        {
            "name": "Alice Johnson",
            "email": "alice.johnson@example.com",
            "phone": "+1-555-123-4567",
            "job_role": "Full Stack Engineer"
        }
    ]

# # Function call and print output
# if _name_ == "_main_":
#     jd = "We are looking for a Senior Software Engineer with experience in Python, Django, and AWS."
#     candidates = getDetails(jd)
    
#     print("\nReturned Candidates:\n")
#     for candidate in candidates:
#         print(candidate)