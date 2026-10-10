from flask import Flask, jsonify, request

import creds
from sql import create_connection, execute_read_query, execute_query


app = Flask(__name__)

myCreds = creds.Creds()

connection = create_connection(
    myCreds.conString,
    myCreds.username,
    myCreds.password,
    myCreds.dbName
)


@app.route("/", methods=["GET"])
def home():
    return "Equipment Rental API is running"


@app.route("/api/customer", methods=["GET"])
def get_customers():
    query = "SELECT * FROM customer"
    customers = execute_read_query(connection, query)

    return jsonify(customers)


@app.route("/api/customer", methods=["POST"])
def add_customer():

    request_data = request.get_json()

    firstname = request_data["firstname"]
    lastname = request_data["lastname"]
    email = request_data["email"]

    query = f"""
        INSERT INTO customer (firstname, lastname, email)
        VALUES ('{firstname}', '{lastname}', '{email}')
    """

    execute_query(connection, query)

    return jsonify({"message": "Customer added successfully"}), 201


@app.route("/api/customer", methods=["PUT"])
def update_customer():

    request_data = request.get_json()

    customerid = request_data["id"]
    firstname = request_data["firstname"]
    lastname = request_data["lastname"]
    email = request_data["email"]

    query = f"""
        UPDATE customer
        SET firstname = '{firstname}',
            lastname = '{lastname}',
            email = '{email}'
        WHERE id = {customerid}
    """

    execute_query(connection, query)

    return jsonify({"message": "Customer updated successfully"})


# DELETE customer
@app.route("/api/customer", methods=["DELETE"])
def delete_customer():
    request_data = request.get_json()

    customerid = request_data["id"]

    query = f"""
        DELETE FROM customer
        WHERE id = {customerid}
    """

    execute_query(connection, query)

    return jsonify({"message": "Customer deleted successfully"})


# READ categories
@app.route("/api/category", methods=["GET"])
def get_categories():
    query = "SELECT * FROM category"
    categories = execute_read_query(connection, query)

    return jsonify(categories)


# CREATE category
@app.route("/api/category", methods=["POST"])
def add_category():
    request_data = request.get_json()

    categoryname = request_data["categoryname"]
    description = request_data["description"]

    query = f"""
        INSERT INTO category (categoryname, description)
        VALUES ('{categoryname}', '{description}')
    """

    execute_query(connection, query)

    return jsonify({"message": "Category added successfully"}), 201


# UPDATE category
@app.route("/api/category", methods=["PUT"])
def update_category():
    request_data = request.get_json()

    categoryid = request_data["id"]
    categoryname = request_data["categoryname"]
    description = request_data["description"]

    query = f"""
        UPDATE category
        SET categoryname = '{categoryname}',
            description = '{description}'
        WHERE id = {categoryid}
    """

    execute_query(connection, query)

    return jsonify({"message": "Category updated successfully"})


# DELETE category
@app.route("/api/category", methods=["DELETE"])
def delete_category():
    request_data = request.get_json()

    categoryid = request_data["id"]

    query = f"""
        DELETE FROM category
        WHERE id = {categoryid}
    """

    execute_query(connection, query)

    return jsonify({"message": "Category deleted successfully"})


# READ equipment
@app.route("/api/equipment", methods=["GET"])
def get_equipment():
    query = "SELECT * FROM equipment"
    equipment = execute_read_query(connection, query)

    return jsonify(equipment)


# CREATE equipment
@app.route("/api/equipment", methods=["POST"])
def add_equipment():
    request_data = request.get_json()

    equipmentname = request_data["equipmentname"]
    categoryid = request_data["categoryid"]
    dailyrate = request_data["dailyrate"]
    quantityavailable = request_data["quantityavailable"]

    query = f"""
        INSERT INTO equipment
        (equipmentname, categoryid, dailyrate, quantityavailable)
        VALUES
        ('{equipmentname}', {categoryid}, {dailyrate}, {quantityavailable})
    """

    execute_query(connection, query)

    return jsonify({"message": "Equipment added successfully"}), 201


# UPDATE equipment
@app.route("/api/equipment", methods=["PUT"])
def update_equipment():
    request_data = request.get_json()

    equipmentid = request_data["id"]
    equipmentname = request_data["equipmentname"]
    categoryid = request_data["categoryid"]
    dailyrate = request_data["dailyrate"]
    quantityavailable = request_data["quantityavailable"]

    query = f"""
        UPDATE equipment
        SET equipmentname = '{equipmentname}',
            categoryid = {categoryid},
            dailyrate = {dailyrate},
            quantityavailable = {quantityavailable}
        WHERE id = {equipmentid}
    """

    execute_query(connection, query)

    return jsonify({"message": "Equipment updated successfully"})


# DELETE equipment
@app.route("/api/equipment", methods=["DELETE"])
def delete_equipment():
    request_data = request.get_json()

    equipmentid = request_data["id"]

    query = f"""
        DELETE FROM equipment
        WHERE id = {equipmentid}
    """

    execute_query(connection, query)

    return jsonify({"message": "Equipment deleted successfully"})


# READ rental transactions
@app.route("/api/rentaltransaction", methods=["GET"])
def get_rental_transactions():
    query = "SELECT * FROM rentaltransaction"
    rentals = execute_read_query(connection, query)

    return jsonify(rentals)


# CREATE rental transaction
@app.route("/api/rentaltransaction", methods=["POST"])
def add_rental_transaction():
    request_data = request.get_json()

    customerid = request_data["customerid"]
    equipmentid = request_data["equipmentid"]
    quantity = request_data["quantity"]

    # Quantity must be greater than zero
    if quantity <= 0:
        return jsonify({"message": "Quantity must be greater than zero"}), 400

    # Make sure customer exists
    customer_query = f"""
        SELECT * FROM customer
        WHERE id = {customerid}
    """

    customer = execute_read_query(connection, customer_query)

    if len(customer) == 0:
        return jsonify({"message": "Customer not found"}), 404

    # Get equipment and current inventory
    equipment_query = f"""
        SELECT * FROM equipment
        WHERE id = {equipmentid}
    """

    equipment = execute_read_query(connection, equipment_query)

    if len(equipment) == 0:
        return jsonify({"message": "Equipment not found"}), 404

    quantityavailable = equipment[0]["quantityavailable"]

    # Business rule: cannot rent more than available
    if quantity > quantityavailable:
        return jsonify({"message": "Insufficient inventory"}), 400

    # Create rental transaction
    rental_query = f"""
        INSERT INTO rentaltransaction
        (customerid, equipmentid, quantity)
        VALUES
        ({customerid}, {equipmentid}, {quantity})
    """

    execute_query(connection, rental_query)

    # Reduce available inventory
    new_quantity = quantityavailable - quantity

    inventory_query = f"""
        UPDATE equipment
        SET quantityavailable = {new_quantity}
        WHERE id = {equipmentid}
    """

    execute_query(connection, inventory_query)

    return jsonify({"message": "Rental created successfully"}), 201


# UPDATE rental transaction
@app.route("/api/rentaltransaction", methods=["PUT"])
def update_rental_transaction():
    request_data = request.get_json()

    rentalid = request_data["id"]
    customerid = request_data["customerid"]
    equipmentid = request_data["equipmentid"]
    quantity = request_data["quantity"]

    if quantity <= 0:
        return jsonify({"message": "Quantity must be greater than zero"}), 400

    # Get existing rental
    rental_query = f"""
        SELECT * FROM rentaltransaction
        WHERE id = {rentalid}
    """

    rental = execute_read_query(connection, rental_query)

    if len(rental) == 0:
        return jsonify({"message": "Rental transaction not found"}), 404

    old_customerid = rental[0]["customerid"]
    old_equipmentid = rental[0]["equipmentid"]
    old_quantity = rental[0]["quantity"]

    # Make sure customer exists
    customer_query = f"""
        SELECT * FROM customer
        WHERE id = {customerid}
    """

    customer = execute_read_query(connection, customer_query)

    if len(customer) == 0:
        return jsonify({"message": "Customer not found"}), 404

    # Make sure equipment exists
    equipment_query = f"""
        SELECT * FROM equipment
        WHERE id = {equipmentid}
    """

    equipment = execute_read_query(connection, equipment_query)

    if len(equipment) == 0:
        return jsonify({"message": "Equipment not found"}), 404

    quantityavailable = equipment[0]["quantityavailable"]

    # Find other rentals for the old customer/equipment
    rented_query = f"""
        SELECT COALESCE(SUM(quantity), 0) AS totalrented
        FROM rentaltransaction
        WHERE customerid = {old_customerid}
        AND equipmentid = {old_equipmentid}
        AND id != {rentalid}
    """

    rented_result = execute_read_query(connection, rented_query)
    other_rentals = int(rented_result[0]["totalrented"])

    # Find returns for the old customer/equipment
    returned_query = f"""
        SELECT COALESCE(SUM(quantity), 0) AS totalreturned
        FROM returntransaction
        WHERE customerid = {old_customerid}
        AND equipmentid = {old_equipmentid}
    """

    returned_result = execute_read_query(connection, returned_query)
    total_returned = int(returned_result[0]["totalreturned"])

    # Check what the old rental group would look like after the update
    if customerid == old_customerid and equipmentid == old_equipmentid:
        rentals_after_update = other_rentals + quantity
    else:
        rentals_after_update = other_rentals

    if total_returned > rentals_after_update:
        return jsonify({
            "message": "Cannot update rental because equipment has already been returned"
        }), 400

    # Update inventory
    if old_equipmentid == equipmentid:
        total_available = quantityavailable + old_quantity

        if quantity > total_available:
            return jsonify({"message": "Insufficient inventory"}), 400

        new_available = total_available - quantity

        inventory_query = f"""
            UPDATE equipment
            SET quantityavailable = {new_available}
            WHERE id = {equipmentid}
        """

        execute_query(connection, inventory_query)

    else:
        if quantity > quantityavailable:
            return jsonify({"message": "Insufficient inventory"}), 400

        restore_query = f"""
            UPDATE equipment
            SET quantityavailable = quantityavailable + {old_quantity}
            WHERE id = {old_equipmentid}
        """

        execute_query(connection, restore_query)

        new_available = quantityavailable - quantity

        inventory_query = f"""
            UPDATE equipment
            SET quantityavailable = {new_available}
            WHERE id = {equipmentid}
        """

        execute_query(connection, inventory_query)

    update_query = f"""
        UPDATE rentaltransaction
        SET customerid = {customerid},
            equipmentid = {equipmentid},
            quantity = {quantity}
        WHERE id = {rentalid}
    """

    execute_query(connection, update_query)

    return jsonify({"message": "Rental transaction updated successfully"})

# DELETE rental transaction
@app.route("/api/rentaltransaction", methods=["DELETE"])
def delete_rental_transaction():
    request_data = request.get_json()

    rentalid = request_data["id"]

    rental_query = f"""
        SELECT * FROM rentaltransaction
        WHERE id = {rentalid}
    """

    rental = execute_read_query(connection, rental_query)

    if len(rental) == 0:
        return jsonify({"message": "Rental transaction not found"}), 404

    customerid = rental[0]["customerid"]
    equipmentid = rental[0]["equipmentid"]
    quantity = rental[0]["quantity"]

    # Find total quantity rented by this customer
    rented_query = f"""
        SELECT COALESCE(SUM(quantity), 0) AS totalrented
        FROM rentaltransaction
        WHERE customerid = {customerid}
        AND equipmentid = {equipmentid}
    """

    rented_result = execute_read_query(connection, rented_query)
    total_rented = int(rented_result[0]["totalrented"])

    # Find total quantity already returned
    returned_query = f"""
        SELECT COALESCE(SUM(quantity), 0) AS totalreturned
        FROM returntransaction
        WHERE customerid = {customerid}
        AND equipmentid = {equipmentid}
    """

    returned_result = execute_read_query(connection, returned_query)
    total_returned = int(returned_result[0]["totalreturned"])

    # Make sure deleting this rental would not make returns greater than rentals
    remaining_rentals = total_rented - quantity

    if total_returned > remaining_rentals:
        return jsonify({
            "message": "Cannot delete rental because equipment has already been returned"
        }), 400

    delete_query = f"""
        DELETE FROM rentaltransaction
        WHERE id = {rentalid}
    """

    execute_query(connection, delete_query)

    # Put the deleted rental quantity back into inventory
    inventory_query = f"""
        UPDATE equipment
        SET quantityavailable = quantityavailable + {quantity}
        WHERE id = {equipmentid}
    """

    execute_query(connection, inventory_query)

    return jsonify({"message": "Rental transaction deleted successfully"})

# READ return transactions
@app.route("/api/returntransaction", methods=["GET"])
def get_return_transactions():
    query = "SELECT * FROM returntransaction"
    returns = execute_read_query(connection, query)

    return jsonify(returns)


# CREATE return transaction
@app.route("/api/returntransaction", methods=["POST"])
def add_return_transaction():
    request_data = request.get_json()

    customerid = request_data["customerid"]
    equipmentid = request_data["equipmentid"]
    quantity = request_data["quantity"]

    if quantity <= 0:
        return jsonify({"message": "Quantity must be greater than zero"}), 400

    # Make sure customer exists
    customer_query = f"""
        SELECT * FROM customer
        WHERE id = {customerid}
    """

    customer = execute_read_query(connection, customer_query)

    if len(customer) == 0:
        return jsonify({"message": "Customer not found"}), 404

    # Make sure equipment exists
    equipment_query = f"""
        SELECT * FROM equipment
        WHERE id = {equipmentid}
    """

    equipment = execute_read_query(connection, equipment_query)

    if len(equipment) == 0:
        return jsonify({"message": "Equipment not found"}), 404

    # Find total quantity rented by this customer
    rented_query = f"""
        SELECT COALESCE(SUM(quantity), 0) AS totalrented
        FROM rentaltransaction
        WHERE customerid = {customerid}
        AND equipmentid = {equipmentid}
    """

    rented_result = execute_read_query(connection, rented_query)
    total_rented = int(rented_result[0]["totalrented"])

    # Find quantity already returned
    returned_query = f"""
        SELECT COALESCE(SUM(quantity), 0) AS totalreturned
        FROM returntransaction
        WHERE customerid = {customerid}
        AND equipmentid = {equipmentid}
    """

    returned_result = execute_read_query(connection, returned_query)
    total_returned = int(returned_result[0]["totalreturned"])

    currently_rented = total_rented - total_returned

    # Business rule: cannot return more than currently rented
    if quantity > currently_rented:
        return jsonify({"message": "Cannot return more equipment than currently rented"}), 400

    # Create return transaction
    return_query = f"""
        INSERT INTO returntransaction
        (customerid, equipmentid, quantity)
        VALUES
        ({customerid}, {equipmentid}, {quantity})
    """

    execute_query(connection, return_query)

    # Put returned equipment back into inventory
    inventory_query = f"""
        UPDATE equipment
        SET quantityavailable = quantityavailable + {quantity}
        WHERE id = {equipmentid}
    """

    execute_query(connection, inventory_query)

    return jsonify({"message": "Return created successfully"}), 201



# UPDATE return transaction
@app.route("/api/returntransaction", methods=["PUT"])
def update_return_transaction():
    request_data = request.get_json()

    returnid = request_data["id"]
    customerid = request_data["customerid"]
    equipmentid = request_data["equipmentid"]
    quantity = request_data["quantity"]

    if quantity <= 0:
        return jsonify({"message": "Quantity must be greater than zero"}), 400

    # Get existing return transaction
    existing_query = f"""
        SELECT * FROM returntransaction
        WHERE id = {returnid}
    """

    existing_return = execute_read_query(connection, existing_query)

    if len(existing_return) == 0:
        return jsonify({"message": "Return transaction not found"}), 404

    old_equipmentid = existing_return[0]["equipmentid"]
    old_quantity = existing_return[0]["quantity"]

    # Find total rented for the new customer/equipment combination
    rented_query = f"""
        SELECT COALESCE(SUM(quantity), 0) AS totalrented
        FROM rentaltransaction
        WHERE customerid = {customerid}
        AND equipmentid = {equipmentid}
    """

    rented_result = execute_read_query(connection, rented_query)
    total_rented = int(rented_result[0]["totalrented"])

    # Find returns except the one currently being updated
    returned_query = f"""
        SELECT COALESCE(SUM(quantity), 0) AS totalreturned
        FROM returntransaction
        WHERE customerid = {customerid}
        AND equipmentid = {equipmentid}
        AND id != {returnid}
    """

    returned_result = execute_read_query(connection, returned_query)
    total_returned = int(returned_result[0]["totalreturned"])

    currently_rented = total_rented - total_returned

    if quantity > currently_rented:
        return jsonify({"message": "Cannot return more equipment than currently rented"}), 400

    # Undo old inventory effect
    undo_inventory_query = f"""
        UPDATE equipment
        SET quantityavailable = quantityavailable - {old_quantity}
        WHERE id = {old_equipmentid}
    """

    execute_query(connection, undo_inventory_query)

    # Apply new inventory effect
    new_inventory_query = f"""
        UPDATE equipment
        SET quantityavailable = quantityavailable + {quantity}
        WHERE id = {equipmentid}
    """

    execute_query(connection, new_inventory_query)

    update_query = f"""
        UPDATE returntransaction
        SET customerid = {customerid},
            equipmentid = {equipmentid},
            quantity = {quantity}
        WHERE id = {returnid}
    """

    execute_query(connection, update_query)

    return jsonify({"message": "Return transaction updated successfully"})


# DELETE return transaction
@app.route("/api/returntransaction", methods=["DELETE"])
def delete_return_transaction():
    request_data = request.get_json()

    returnid = request_data["id"]

    return_query = f"""
        SELECT * FROM returntransaction
        WHERE id = {returnid}
    """

    return_record = execute_read_query(connection, return_query)

    if len(return_record) == 0:
        return jsonify({"message": "Return transaction not found"}), 404

    equipmentid = return_record[0]["equipmentid"]
    quantity = return_record[0]["quantity"]

    delete_query = f"""
        DELETE FROM returntransaction
        WHERE id = {returnid}
    """

    execute_query(connection, delete_query)

    # Removing a return means those units are no longer considered returned
    inventory_query = f"""
        UPDATE equipment
        SET quantityavailable = quantityavailable - {quantity}
        WHERE id = {equipmentid}
    """

    execute_query(connection, inventory_query)

    return jsonify({"message": "Return transaction deleted successfully"})



# VIEW customer rentals
@app.route("/api/customer/rentals", methods=["GET"])
def get_customer_rentals():
    customerid = request.args.get("customerid")

    query = f"""
        SELECT rentaltransaction.id,
               rentaltransaction.date,
               rentaltransaction.customerid,
               rentaltransaction.equipmentid,
               equipment.equipmentname,
               rentaltransaction.quantity
        FROM rentaltransaction
        JOIN equipment
        ON rentaltransaction.equipmentid = equipment.id
        WHERE rentaltransaction.customerid = {customerid}
    """

    rentals = execute_read_query(connection, query)

    return jsonify(rentals)


# VIEW current inventory
@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    query = """
        SELECT equipment.id,
               equipment.equipmentname,
               category.categoryname,
               equipment.dailyrate,
               equipment.quantityavailable
        FROM equipment
        JOIN category
        ON equipment.categoryid = category.id
    """

    inventory = execute_read_query(connection, query)

    return jsonify(inventory)


if __name__ == "__main__":
    app.run(debug=True)