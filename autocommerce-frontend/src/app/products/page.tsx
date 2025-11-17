"use client";

import { useEffect, useState } from "react";

interface Product {
  id: number;
  name: string;
  price: number;
  currency: string;
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchProducts() {
      try {
        const res = await fetch(
          "https://fer333444-autocommerce-ai.onrender.com/api/products/"
        );
        const data = await res.json();
        setProducts(data);
      } catch (error) {
        console.error("Error cargando productos:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchProducts();
  }, []);

  if (loading) {
    return <p className="text-center mt-10 text-xl">Cargando productos...</p>;
  }

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold mb-6">Productos disponibles</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {products.map((p) => (
          <div
            key={p.id}
            className="border border-gray-700 p-6 rounded-xl shadow bg-gray-900"
          >
            <h2 className="text-xl font-semibold">{p.name}</h2>
            <p className="text-lg mt-2">
              {p.price} {p.currency}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

