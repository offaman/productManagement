import math
def paginate(org_id, current_page_number, max_record_per_page, total_records, baseURL, taxonomy_id = None):
    
    pagingURL = {
        "previous_page":"",
        "next_page":""
    }
    if total_records % max_record_per_page:
        max_page_possible  = math.ceil(total_records /  max_record_per_page)
    else:
        max_page_possible = 1

    page_number = 0
    if current_page_number > max_page_possible:
        page_number = max_page_possible 
    else:
        page_number = current_page_number

    remaining_record_after_pagination = total_records - (current_page_number * max_record_per_page)

    if taxonomy_id:
        if current_page_number == max_page_possible and current_page_number > 2:
            pagingURL['previous_page'] = baseURL.format(org_id = org_id, page_index = max_page_possible-1, taxonomy_id = taxonomy_id)
        elif current_page_number <= 1:
            pass
        else:
            pagingURL['previous_page'] = baseURL.format(org_id = org_id, page_index = current_page_number - 1,taxonomy_id = taxonomy_id)

        if remaining_record_after_pagination > 0:
            pagingURL['next_page']  = baseURL.format(org_id = org_id, page_index = page_number + 1,taxonomy_id = taxonomy_id)
    else:
        if current_page_number == max_page_possible and current_page_number > 2:
            pagingURL['previous_page'] = baseURL.format(org_id = org_id, page_index = max_page_possible-1)
        elif current_page_number <= 1:
            pass
        else:
            pagingURL['previous_page'] = baseURL.format(org_id = org_id, page_index = current_page_number - 1)
            
        if remaining_record_after_pagination > 0:
            pagingURL['next_page']  = baseURL.format(org_id = org_id, page_index = current_page_number + 1)
    
    return pagingURL