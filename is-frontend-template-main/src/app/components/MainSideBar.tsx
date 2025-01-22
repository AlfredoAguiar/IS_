"use client";

import React, { useRef, useState } from "react";
import {
  List,
  ListItem,
  ListItemText,
  Box,
  ListSubheader,
  ListItemButton,
  TextField,
  Button,
} from "@mui/material";
import UploadFilesDialog from "./UploadFilesDialog";
import XmlViewerDialog from "./XmlViewer";
import { Search } from "@mui/icons-material";
import { redirect } from "next/navigation";
import UpdateCarDialog from "./Updatecar";

// Define the type for the search form state
interface SearchForm {
  city: string;
}

const Sidebar = ({ searchValue }: { searchValue: string }) => {
  const uploadFilesDialogRef = useRef<any>(null);
  const xmlViewerDialog = useRef<any>(null);
  const updateCarDialog = useRef<any>(null);

  const [searchByCityForm, setSearchByCityForm] = useState<SearchForm>({
    city: searchValue,
  });

  // Open the UploadFilesDialog
  const handleOpenUploadFilesDialog = () => {
    if (uploadFilesDialogRef.current) {
      uploadFilesDialogRef.current.handleClickOpen();
    }
  };

  // Open the XmlViewerDialog
  const handleXmlViewerDialog = () => {
    if (xmlViewerDialog.current) {
      xmlViewerDialog.current.handleClickOpen();
    }
  };

  // Form submission handler for city search
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    redirect(`/?search=${searchByCityForm.city}`);
  };

  // Open the UpdateCarDialog
  const handleUpdateCarDialog = () => {
    if (updateCarDialog.current) {
      updateCarDialog.current.handleClickOpen();
    }
  };

  return (
    <>
      <UploadFilesDialog ref={uploadFilesDialogRef} />
      <XmlViewerDialog ref={xmlViewerDialog} />
      <UpdateCarDialog ref={updateCarDialog} />

      <List
        sx={{ width: "100%", maxWidth: 360, bgcolor: "background.paper" }}
        component="nav"
        aria-labelledby="nested-list-subheader"
        subheader={
          <ListSubheader
            className="text-black font-bold border-b-2"
            component="div"
            id="nested-list-subheader"
          >
            <p className="text-gray-700 font-bold text-xl my-4">IS - FINAL</p>
          </ListSubheader>
        }
      >

        <ListItemButton onClick={handleOpenUploadFilesDialog}>
          <ListItemText className="text-gray-600" primary="Upload File" />
        </ListItemButton>
        <ListItemButton onClick={handleXmlViewerDialog}>
          <ListItemText className="text-gray-600" primary="XMLs" />
        </ListItemButton>
        <ListItemButton onClick={handleUpdateCarDialog}>
          <ListItemText className="text-gray-600" primary="Update car seller" />
        </ListItemButton>
      </List>
    </>
  );
};

export default Sidebar;
