import React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { Box, Typography } from '@mui/material';
import { toast } from 'react-toastify';

const UploadFilesDialog = React.forwardRef((props, ref) => {
  const [open, setOpen] = React.useState(false);
  const [file, setFile] = React.useState<any>(null);
  const [loading, setLoading] = React.useState<boolean>(false);

  const handleFileChange = (event: any) => {
    const uploadedFile = event.target.files[0];
    setFile(uploadedFile);
  };

  const handleRemoveFile = () => {
    setFile(null);
  };

  React.useImperativeHandle(ref, () => ({
    handleClickOpen() {
      setOpen(true);
    },
  }));

  const handleClose = () => {
    setOpen(false);
  };

  const handleSubmit = async () => {
  if (!file) {
    toast.error('Please select a file to upload.');
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  // Log form data for debugging
  for (let [key, value] of formData.entries()) {
    console.log(`${key}:`, value);
  }

  setLoading(true);

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Error:', errorData);
      toast.error(errorData.message || 'Failed to upload file.');
    } else {
      toast.success("File uploaded successfully!");
      handleClose();
    }
  } catch (error) {
    console.error('Error:', error);
    toast.error("An error occurred while uploading the file.");
  } finally {
    setLoading(false);
  }
};

  return (
    <React.Fragment>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          {"Upload File"}
        </DialogTitle>
        <DialogContent>
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
              p: 3,
              border: "1px solid #ccc",
              borderRadius: "8px",
            }}
          >
            {/* Upload .csv file */}
            <Typography variant="h6">Upload .csv file</Typography>
            {file ? (
              <>
                <Typography variant="body1">
                  Selected File: {file.name}
                </Typography>
                <Button variant="contained" color="error" onClick={handleRemoveFile}>
                  Remove File
                </Button>
              </>
            ) : (
              <Button
                variant="contained"
                component="label"
              >
                Select .csv file
                <input
                  type="file"
                  hidden
                  onChange={handleFileChange}
                  accept=".csv"
                />
              </Button>
            )}

            {/* Loading state */}
            {loading && <Typography variant="body2">Uploading...</Typography>}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button
            disabled={loading || !file}
            onClick={handleSubmit}
            autoFocus
          >
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
});

export default UploadFilesDialog;