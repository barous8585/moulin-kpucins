import streamlit as st
import pandas as pd
from db import SessionLocal, engine
from models import Product, create_tables
from models import Sale
from collections import Counter
from ticket import generate_ticket


create_tables(engine)

st.title("Le Moulin des K'pucins - Gestion")
session = SessionLocal()

CATEGORIES = ["Pain", "Viennoiseries", "Sandwichs", "Boissons"]

menu = st.sidebar.selectbox(
    "Menu",
    ["Voir Produits", "Ajouter Produit", "Caisse", "Statistiques"]
)


# ---- VOIR PRODUITS ----
if menu == "Voir Produits":
    produits = session.query(Product).all()

    for p in produits:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 2])

        col1.write(p.name)
        col2.write(f"{p.stock}")

        if p.stock == 0:
            col3.error("Rupture ❌")
        elif p.stock <= p.alert_threshold:
            col3.warning("Stock bas ⚠️")
        else:
            col3.success("OK")

        col4.write(f"Seuil : {p.alert_threshold}")


# ---- AJOUTER PRODUIT ----
elif menu == "Ajouter Produit":
    with st.form("form_add"):
        name = st.text_input("Nom du produit")
        category = st.selectbox("Catégorie", CATEGORIES)
        price = st.number_input("Prix (€)", min_value=0.0)
        stock = st.number_input("Stock initial", min_value=0, step=1)
        submitted = st.form_submit_button("Ajouter")

        if submitted:
            session.add(Product(
                name=name,
                category=category,
                price=price,
                stock=stock

            ))
            session.commit()
            st.success("Produit ajouté")
            alert_threshold = st.number_input(
                "Seuil d'alerte stock",
                min_value=1,
                step=1,
                value=5
            )
            alert_threshold = alert_threshold



# ---- CAISSE ----
elif menu == "Caisse":
    st.header("🧾 Caisse rapide")

    if "panier" not in st.session_state:
        st.session_state.panier = []

    produits = session.query(Product).all()
    categories = sorted(set(p.category for p in produits))

    for cat in categories:
        st.subheader(cat)
        cols = st.columns(3)
        prods_cat = [p for p in produits if p.category == cat]

        for i, p in enumerate(prods_cat):
            if p.stock == 0:
                cols[i % 3].button(
                    f"{p.name} – RUPTURE",
                    disabled=True,
                    key=f"rupture_{p.id}"
                )

            else:
                if cols[i % 3].button(
                        f"{p.name} – {p.price:.2f} € (Stock {p.stock})",
                        key=f"add_{p.id}"
                ):
                    st.session_state.panier.append(p)

    st.divider()
    st.subheader("🛍️ Panier")

    if st.session_state.panier:
        total = sum(p.price for p in st.session_state.panier)
        for p in st.session_state.panier:
            st.write(f"- {p.name} ({p.price:.2f} €)")

        st.markdown(f"### 💰 Total : **{total:.2f} €**")

        col1, col2 = st.columns(2)

        if col1.button("❌ Vider"):
            st.session_state.panier = []
            st.rerun()

        if col2.button("✅ Encaisser"):
            from collections import Counter

            total = sum(p.price for p in st.session_state.panier)
            noms = [p.name for p in st.session_state.panier]
            details = ", ".join(f"{k} x{v}" for k, v in Counter(noms).items())

            # enregistrer la vente
            sale = Sale(total=total, details=details)
            session.add(sale)

            # décrémenter le stock
            for p in st.session_state.panier:
                prod = session.query(Product).get(p.id)
                if prod.stock > 0:
                    prod.stock -= 1

            session.commit()

            # générer le ticket PDF
            ticket_path = generate_ticket(details, total)

            st.success("Paiement enregistré – ticket généré 🧾")

            with open(ticket_path, "rb") as f:
                st.download_button(
                    label="📄 Télécharger le ticket",
                    data=f,
                    file_name=ticket_path.split("/")[-1],
                    mime="application/pdf"
                )

            st.session_state.panier = []


elif menu == "Historique":
    st.header("📊 Historique des ventes")

    ventes = session.query(Sale).order_by(Sale.date.desc()).all()

    if ventes:
        for v in ventes:
            st.markdown(
                f"""
                **🧾 Vente #{v.id}**  
                📅 {v.date.strftime('%d/%m/%Y %H:%M')}  
                🛍️ {v.details}  
                💰 **Total : {v.total:.2f} €**
                """
            )
            st.divider()
    else:
        st.info("Aucune vente enregistrée")

elif menu == "Statistiques":
    st.subheader("📊 Statistiques de vente")

    import pandas as pd
    from datetime import date, datetime, timedelta

    ventes = session.query(Sale).all()

    if not ventes:
        st.info("Aucune vente enregistrée pour le moment.")
    else:
        # ---- DataFrame ----
        data = [{
            "date": v.date,
            "total": v.total,
            "details": v.details
        } for v in ventes]

        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])

        # ---- Filtres période ----
        col1, col2 = st.columns(2)

        with col1:
            debut = st.date_input("Date de début", value=date.today() - timedelta(days=7))
        with col2:
            fin = st.date_input("Date de fin", value=date.today())

        mask = (df["date"].dt.date >= debut) & (df["date"].dt.date <= fin)
        df_filtre = df.loc[mask]

        # ---- KPI ----
        total_ca = df_filtre["total"].sum()
        nb_ventes = len(df_filtre)

        col1, col2 = st.columns(2)
        col1.metric("💰 Chiffre d'affaires", f"{total_ca:.2f} €")
        col2.metric("🧾 Nombre de ventes", nb_ventes)

        st.divider()

        # ---- CA par jour ----
        ca_jour = (
            df_filtre
            .groupby(df_filtre["date"].dt.date)["total"]
            .sum()
            .reset_index()
            .rename(columns={"date": "Jour", "total": "CA (€)"})
        )

        st.subheader("📆 CA par jour")
        st.bar_chart(ca_jour.set_index("Jour"))

        st.divider()

        # ---- Top produits ----
        produits = []

        for d in df_filtre["details"]:
            for item in d.split(","):
                nom, qty = item.strip().rsplit(" x", 1)
                produits.extend([nom] * int(qty))

        if produits:
            top = (
                pd.Series(produits)
                .value_counts()
                .reset_index()
                .rename(columns={"index": "Produit", 0: "Quantité"})
            )

            st.subheader("🥇 Produits les plus vendus")
            st.dataframe(top)
        else:
            st.info("Pas assez de données pour le top produits.")
