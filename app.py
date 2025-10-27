import streamlit as st
from datetime import datetime

st.title("🚚 Donate - Home Delivery")

st.markdown("""
    **Home Delivery Service:** We will collect your donation from your location. Please provide your details below and we arrange the pickup. Our service is available across Sri Lanka.
    """)

with st.form("delivery_donation"):
    st.subheader("1. Donor Information")

    col1, col2 = st.columns(2)
    with col1:
        donor_name = st.text_input("Your Name*", placeholder="Enter your full name")
        email = st.text_input("Email (Optional)", placeholder="your@email.com")

    with col2:
        phone = st.text_input("Phone Number*", placeholder="07XXXXXXXX")
        district = st.selectbox("District", [
            "Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Nuwara Eliya",
            "Galle", "Matara", "Hambantota", "Jaffna", "Kilinochchi", "Mannar",
            "Vavuniya", "Mullaitivu", "Batticaloa", "Ampara", "Trincomalee",
            "Kurunegala", "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla",
            "Monaragala", "Ratnapura", "Kegalle"
        ])

    address = st.text_area("Delivery Address*",
                           placeholder="Enter your complete address including street, city, and landmarks...",
                           height=100)

    st.subheader("2. Donation Items")
    st.markdown("**Select products and quantities:**")

    # Search functionality
    search_term = st.text_input("Search", placeholder="Search products...")

    # Product selection
    try:
        cursor.execute("SELECT * FROM inventory")
        products = cursor.fetchall()

        # Filter products based on search
        if search_term:
            filtered_products = [p for p in products if search_term.lower() in p[1].lower()]
        else:
            filtered_products = products

        selected_products = []
        total_amount = 0

        # Display products in a clean layout
        for product in filtered_products:
            col1, col2, col3 = st.columns([3, 1, 2])
            with col1:
                st.write(f"**{product[1]}**")
                st.write(f"Price: LKR {product[2]:,.2f}")
            with col2:
                qty = st.number_input("Qty",
                                      min_value=0,
                                      max_value=min(20, product[3]),
                                      key=f"delivery_{product[0]}")
            with col3:
                if qty > 0:
                    product_total = product[2] * qty
                    selected_products.append({
                        "name": product[1],
                        "quantity": qty,
                        "total": product_total,
                        "product_id": product[0]
                    })
                    total_amount += product_total
                    st.success(f"LKR {product_total:,.2f}")

        # Display donation summary
        if selected_products:
            st.subheader("💰 Donation Summary")
            for item in selected_products:
                st.write(f"• {item['name']} x {item['quantity']} = LKR {item['total']:,.2f}")
            st.write(f"**Total Donation Value:** LKR {total_amount:,.2f}")

        submitted = st.form_submit_button("📦 Schedule Pickup")

        if submitted:
            if not donor_name or not phone or not address:
                st.error("❌ Please fill all required fields (*)")
            elif total_amount == 0:
                st.error("❌ Please select at least one product to donate")
            elif not validate_phone(phone):
                st.error("❌ Please enter a valid 10-digit phone number")
            else:
                # Format products string
                products_str = " | ".join([f"{item['name']} x {item['quantity']}" for item in selected_products])

                try:
                    # First update the database table structure if needed
                    cursor.execute('''
                            CREATE TABLE IF NOT EXISTS delivery_donations (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                donor_name TEXT,
                                email TEXT,
                                phone TEXT,
                                district TEXT,
                                address TEXT,
                                products TEXT,
                                total_amount REAL,
                                status TEXT DEFAULT 'Pending',
                                timestamp TEXT
                            )
                        ''')

                    # Insert the delivery donation data
                    cursor.execute(
                        "INSERT INTO delivery_donations (donor_name, email, phone, district, address, products, total_amount, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (donor_name, email, phone, district, address, products_str, total_amount,
                         datetime.now().isoformat())
                    )

                    # Update inventory stock
                    for item in selected_products:
                        cursor.execute(
                            "UPDATE inventory SET stock = stock - ? WHERE product_id = ?",
                            (item['quantity'], item['product_id'])
                        )

                    conn.commit()

                    st.success(
                        "🎉 Thank you for your donation! We will contact you within 24 hours to schedule the pickup.")
                    st.balloons()

                    # Show confirmation details
                    st.info(f"""
                        **📋 Pickup Confirmation:**
                        - **Name:** {donor_name}
                        - **Phone:** {phone}
                        - **Email:** {email if email else 'Not provided'}
                        - **District:** {district}
                        - **Address:** {address}
                        - **Donation Items:** {products_str}
                        - **Total Value:** LKR {total_amount:,.2f}
                        - **Reference ID:** {cursor.lastrowid}
                        """)

                except Exception as e:
                    st.error(f"❌ Error scheduling pickup: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error loading products: {str(e)}")