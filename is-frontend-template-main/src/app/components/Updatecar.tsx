"use client";

import React, { useState, forwardRef, useImperativeHandle } from "react";
import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet-defaulticon-compatibility";
import { toast } from "react-toastify";
import axios from "axios";
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button } from "@mui/material";

const UpdateCarDialog = forwardRef((props, ref) => {
  const [open, setOpen] = useState(false);
  const [vin, setVin] = useState<string>("");
  const [sellingPrice, setSellingPrice] = useState<number>(0);
  const [sellerState, setSellerState] = useState<string>("");
  const [saleDate, setSaleDate] = useState<string>("");
  const [sellerName, setSellerName] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  // Expose the `handleClickOpen` method to parent via ref
  useImperativeHandle(ref, () => ({
    handleClickOpen() {
      setOpen(true);
    },
  }));

  const handleClose = () => {
    setOpen(false);
    resetForm();
  };

  const resetForm = () => {
    setVin("");
    setSellingPrice(0);
    setSellerState("");
    setSaleDate("");
    setSellerName(""); // Reset seller_name
    setLoading(false);
  };

  const handleSubmit = async () => {
    if (!vin || !sellingPrice || !sellerState || !saleDate || !sellerName) {
      toast.error("Please fill out all fields before submitting.");
      return;
    }

    if (sellingPrice <= 0) {
      toast.error("Selling price must be greater than 0.");
      return;
    }

    setLoading(true);

    try {
      const response = await axios.put(`/api/updateCar`, {
        vin: vin,
        seller_name: sellerName,
        seller_state: sellerState,
        sale_date: saleDate,
        selling_price: sellingPrice,
      });

      if (response.status === 200) {
        toast.success("Car updated successfully!");
        handleClose();
      } else {
        toast.error("Failed to update car. Please try again.");
      }
    } catch (error) {
      console.error("Error submitting car details:", error);
      toast.error( "An error occurred while updating the car.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      aria-labelledby="create-car-dialog-title"
    >
      <DialogTitle id="create-car-dialog-title">Create Car</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          margin="dense"
          id="vin"
          label="VIN"
          type="text"
          fullWidth
          value={vin}
          onChange={(e) => setVin(e.target.value)}
          aria-label="VIN"
          required
        />
        <TextField
          margin="dense"
          id="seller_name"
          label="Seller Name" // New input for seller name
          type="text"
          fullWidth
          value={sellerName}
          onChange={(e) => setSellerName(e.target.value)} // Update state for seller name
          aria-label="Seller Name"
          required
        />
        <TextField
          margin="dense"
          id="selling_price"
          label="Selling Price"
          type="number"
          fullWidth
          value={sellingPrice}
          onChange={(e) => setSellingPrice(parseFloat(e.target.value))}
          aria-label="Selling Price"
          required
        />
        <TextField
          margin="dense"
          id="seller_state"
          label="Seller State"
          type="text"
          fullWidth
          value={sellerState}
          onChange={(e) => setSellerState(e.target.value)}
          aria-label="Seller State"
          required
        />
        <TextField
          margin="dense"
          id="sale_date"
          label="Sale Date"
          type="date"
          fullWidth
          value={saleDate}
          onChange={(e) => setSaleDate(e.target.value)}
          aria-label="Sale Date"
          InputLabelProps={{
            shrink: true,
          }}
          required
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose} color="primary" disabled={loading}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          color="primary"
          disabled={loading}
          autoFocus
        >
          {loading ? "Saving..." : "Create"}
        </Button>
      </DialogActions>
    </Dialog>
  );
});

export default UpdateCarDialog;
