import streamlit as st
from db import SessionLocal, engine
from models import Product, create_tables

create_tables(engine)

st.set_page_config(page_title="Le Moulin des K'pucins", layout="centered")

st.title("🥖 Le Moulin des K'pucins")
st.subheader("Boulangerie artisanale – Angers")

session = SessionLocal()

categories = session.query(Product.category).distinct().all()

for (cat,) in categories:
    st.divider()
    st.subheader(cat)

    produits = session.query(Product).filter(Product.category == cat).all()

    for p in produits:
        col1, col2 = st.columns([3, 1])
        col1.write(p.name)
        col2.write(f"{p.price:.2f} €")
