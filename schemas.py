"""
Database Schemas for Snowboard Affiliate Site

Each Pydantic model represents a MongoDB collection.
Collection name is the lowercase of the class name.

We store products (snowboards) and reviews. Reviews reference a product by its
string product_id (the inserted id of the product document).
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

class Snowboardproduct(BaseModel):
    """
    Snowboard products that appear on the site.
    Collection name: "snowboardproduct"
    """
    naam: str = Field(..., description="Naam van het snowboard")
    merk: str = Field(..., description="Merk")
    stijl: str = Field(..., description="Rijstijl, bijv. freestyle, all-mountain, park")
    prijseur: float = Field(..., ge=0, description="Prijs in euro")
    beschrijving: Optional[str] = Field(None, description="Korte beschrijving")
    afbeelding_url: Optional[HttpUrl] = Field(None, description="Afbeeldings-URL")
    affiliate_url: Optional[HttpUrl] = Field(None, description="Affiliate link naar webshop")
    gemiddelde_rating: Optional[float] = Field(None, ge=0, le=5, description="Gemiddelde beoordeling (0-5)")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags zoals 'jib', 'buttery', 'stiff'")

class Review(BaseModel):
    """
    Reviews die gebruikers kunnen plaatsen over een product.
    Collection name: "review"
    """
    product_id: str = Field(..., description="ID van het product (string)")
    auteur: str = Field(..., description="Naam of nickname")
    niveau: str = Field(..., description="Niveau: beginner/gevorderd/expert")
    rating: int = Field(..., ge=1, le=5, description="Beoordeling 1-5")
    pluspunten: Optional[str] = Field(None, description="Wat is top")
    minpunten: Optional[str] = Field(None, description="Wat kan beter")
    review_tekst: Optional[str] = Field(None, description="Vrije tekst")
