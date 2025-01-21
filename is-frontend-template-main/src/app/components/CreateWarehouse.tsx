"use client"

import React from 'react';

import "leaflet/dist/leaflet.css";
import "leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css";
import "leaflet-defaulticon-compatibility";
import { toast } from 'react-toastify';
import axios from 'axios';
import { Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button } from '@mui/material';

const CreateCarDialog = React.forwardRef((props, ref) => {
    const [open, setOpen] = React.useState(false);
    
    const [name, setName]         = React.useState<string>('');
    const [latitude, setLatitude] = React.useState<number>(0);
    const [longitude, setLongitude] = React.useState<number>(0);
    const [loading, setLoading]   = React.useState<boolean>(false);
    
    React.useImperativeHandle(ref, () => ({
        handleClickOpen() {
            setOpen(true)
        }
    }))
    
    const handleClose = () => {
        setOpen(false);
    }
    
    const handleSubmit = async () => {
        setLoading(true)
    
        try {
            const response = await axios.post("/api/createCar/", {
                name: name,
                latitude: latitude,
                longitude: longitude
            })
    
            if (response.data) {
                toast.success("Car created successfully!");
                handleClose();
            } else {
                toast.error("Failed to create Car.");
            }
        } catch (error) {
            console.error(error);
            toast.error("An error occurred while creating the car.");
        } finally {
            setLoading(false);
        }
    }
    
    return (
        <React.Fragment>
        <Dialog
            open={open}
            onClose={handleClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
        >
            <DialogTitle id="alert-dialog-title">Create Car</DialogTitle>
            <DialogContent>
            <TextField
                autoFocus
                margin="dense"
                id="name"
                label="Name"
                type="text"
                fullWidth
                value={name}
                onChange={(e) => setName(e.target.value)}
            />
            <TextField
                margin="dense"
                id="latitude"
                label="Latitude"
                type="number"
                fullWidth
                value={latitude}
                onChange={(e) => setLatitude(parseFloat(e.target.value))}
            />
            <TextField
                margin="dense"
                id="longitude"
                label="Longitude"
                type="number"
                fullWidth
                value={longitude}
                onChange={(e) => setLongitude(parseFloat(e.target.value))}
            />
            </DialogContent>
            <DialogActions>
            <Button onClick={handleClose} color="primary">
                Cancel
            </Button>
            <Button disabled={loading === true}  onClick={handleSubmit} autoFocus>
                Create
            </Button>
            </DialogActions>
        </Dialog>
        </React.Fragment>
    );
})

export default CreateCarDialog;
