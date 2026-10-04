from schema import Receipt

def compute_split(receipt:Receipt,num_people:int)->dict:
    if num_people<1: 
        raise ValueError("num_people must be atleast 1") 
    if receipt.subtotal is not None:
        subtotal=receipt.subtotal 
    else:
        subtotal=sum(item.line_total for item in receipt.items)
    per_person=round(receipt.total/num_people,2) 
    return {
        "subtotal":subtotal,
        "tax":receipt.tax,
        "total":receipt.total,
        "per_person":per_person, 
        "num_people":num_people,
        "currency":receipt.currency,
        "items":receipt.items,
    }            

if __name__ == "__main__":
    from schema import LineItem
    r = Receipt(
        merchant="Test",
        currency="CHF",
        items=[
            LineItem(name="Coffee", quantity=2, unit_price=4.5, line_total=9.0),
            LineItem(name="Cake", quantity=1, unit_price=5.5, line_total=5.5),
        ],
        total=14.5,
    )
    print(compute_split(r, 2))