"use client";

import * as React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { Box, Tab, Tabs, TextField } from '@mui/material';
import { Search } from '@mui/icons-material';
import { toast, ToastContainer } from 'react-toastify';
import { ReactElement } from 'react';
import 'react-toastify/dist/ReactToastify.css';

interface SearchForms {
  car: string;
  make: string;
  model: string;
  Year: number;
  min_price: string;
  max_price: string;
  Condition: number;
  vin : string;
}

const XmlViewerDialog = React.forwardRef((_, ref) => {
  const [open, setOpen] = React.useState(false);
  const [value, setValue] = React.useState(0);
  const [xmlContent, setXmlContent] = React.useState<string>("");
  const [isLoading, setIsLoading] = React.useState(false);

  const [searchForms, setSearchForms] = React.useState<SearchForms>({
    car: '',
    make: '',
    model: '',
    Year: 0,
    min_price: '',
    max_price: '',
    Condition: 0,
    vin: '',
  });

  const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
    setXmlContent("");
  };

  React.useImperativeHandle(ref, () => ({
    handleClickOpen() {
      setOpen(true);
    }
  }));

  const handleClose = () => {
    setOpen(false);
    setXmlContent("");
    setSearchForms({
      car: '',
      make: '',
      model: '',
      Year: 0,
      min_price: '',
      max_price: '',
      Condition: 0,
      vin: '',
    });
  };

  const formatXML = (xml: string): ReactElement[] => {
    const lines = xml.split('\n').filter(line => line.trim());
    const elements: ReactElement[] = [];
    let currentBlock: ReactElement[] = [];

    lines.forEach((line, index) => {
      const cleanLine = line.replace(/\\n/g, '').trim();

      if (cleanLine.startsWith('<sale>')) {
        if (currentBlock.length > 0) {
          elements.push(
            <div key={`block-${elements.length}`} style={{ marginBottom: '1rem' }}>
              {currentBlock}
            </div>
          );
          currentBlock = [];
        }
      }

      const lineStyle = cleanLine.startsWith('</') || cleanLine.startsWith('<')
        ? { color: '#569CD6' }
        : { color: '#CE9178' };
      currentBlock.push(
        <div key={`${index}-${cleanLine}`} style={lineStyle}>
          {cleanLine}
        </div>
      );
    });

    if (currentBlock.length > 0) {
      elements.push(
        <div key={`block-${elements.length}`} style={{ marginBottom: '1rem' }}>
          {currentBlock}
        </div>
      );
    }

    return elements;
  };

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setIsLoading(true);
  setXmlContent(""); // Clear previous XML content

  try {
  let url = '';
  const { make, model, min_price, max_price, Year, Condition, vin } = searchForms;


  if (value === 0) {
    url = `/api/xml/filter-by-make-model/?make=${encodeURIComponent(make)}&model=${encodeURIComponent(model)}`;
  } else if (value === 1) {
    url = `/api/xml/filter-by-price/?min_price=${encodeURIComponent(min_price)}&max_price=${encodeURIComponent(max_price)}`;
  } else if (value === 2) {
    url = `/api/xml/filter-by-Year-Condition/?year=${encodeURIComponent(Year)}&condition=${encodeURIComponent(Condition)}`;
  } else if (value === 3) {
    url = `/api/xml/all-cars`;
  } else if (value === 4) {
    url = `/api/xml/filter-by-vin/?vin=${encodeURIComponent(vin)}`;
  } else if (value === 5) {
    url = `/api/xml/deleteCarByVin/?vin=${encodeURIComponent(vin)}`;
  }

  // Adjust method for delete request
  const method = value === 5 ? 'DELETE' : 'GET'; // Use DELETE for delete action

  const response = await fetch(url, {
    method: method, // DELETE for deleting, GET for other actions
    headers: {
      'Content-Type': 'application/json',
    },
  });

    if (!response.ok) {
      throw new Error('Failed to fetch data from the server');
    }

    const data = await response.json();
    const formattedJSON = JSON.stringify(data, null, 2);
    setXmlContent(formattedJSON); // Display JSON as formatted text
  } catch (error) {
    toast.error(error instanceof Error ? error.message : 'An error occurred');
    console.error('Submit error:', error);
  } finally {
    setIsLoading(false);
  }
};
  function CustomTabPanel(props: { children?: React.ReactNode; index: number; value: number; }) {
    const { children, value, index, ...other } = props;

    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`simple-tabpanel-${index}`}
        aria-labelledby={`simple-tab-${index}`}
        {...other}
      >
        {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
      </div>
    );
  }

  function a11yProps(index: number) {
    return {
      'aria-controls': `simple-tabpanel-${index}`,
    };
  }

  return (
    <React.Fragment>
      <ToastContainer />
      <Dialog
        open={open}
        onClose={handleClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>XML Viewer</DialogTitle>
        <DialogContent>
          <Tabs value={value} onChange={handleChange}>
            <Tab label="Search By Make/Model" {...a11yProps(0)} />
            <Tab label="Search By Price" {...a11yProps(1)} />
            <Tab label="Search By Year/Condition" {...a11yProps(2)} />
            <Tab label="All Cars " {...a11yProps(3)} />
            <Tab label="Search By vin " {...a11yProps(4)} />
            <Tab label="Delete " {...a11yProps(5)} />
          </Tabs>


          <CustomTabPanel value={value} index={0}>
            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                label="Car Make"
                fullWidth
                margin="normal"
                value={searchForms.make}
                onChange={(e) => setSearchForms((prev) => ({ ...prev, make: e.target.value }))}
                required
                helperText={!searchForms.make ? "Car make is required" : ""}
                error={!searchForms.make}
              />
              <TextField
                label="Car Model"
                fullWidth
                margin="normal"
                value={searchForms.model}
                onChange={(e) => setSearchForms((prev) => ({ ...prev, model: e.target.value }))}
                required
                helperText={!searchForms.model ? "Car model is required" : ""}
                error={!searchForms.model}
              />
              <Button
                fullWidth
                type="submit"
                variant="contained"
                startIcon={<Search />}
                disabled={isLoading || !searchForms.make.trim() || !searchForms.model.trim()}
              >
                Search
              </Button>
            </Box>
          </CustomTabPanel>

          <CustomTabPanel value={value} index={1}>
            <Box component="form" onSubmit={handleSubmit}>
            <TextField
              label="Min Price"
              fullWidth
              margin="normal"
              value={searchForms.min_price}
              onChange={(e) => setSearchForms((prev) => ({ ...prev, min_price: e.target.value }))}
              required
              helperText={!searchForms.min_price ? "Min price is required" : ""}
              error={!searchForms.min_price}
            />
            <TextField
              label="Max Price"
              fullWidth
              margin="normal"
              value={searchForms.max_price}
              onChange={(e) => setSearchForms((prev) => ({ ...prev, max_price: e.target.value }))}
              required
              helperText={!searchForms.max_price ? "Max price is required" : ""}
              error={!searchForms.max_price}
            />
            <Button
              fullWidth
              type="submit"
              variant="contained"
              startIcon={<Search />}
              disabled={isLoading || !searchForms.min_price.trim() || !searchForms.max_price.trim()}
            >
              Search
            </Button>
            </Box>
          </CustomTabPanel>

<CustomTabPanel value={value} index={2}>
   <Box component="form" onSubmit={handleSubmit}>
            <TextField
              label="Car Year"
              fullWidth
              margin="normal"
              value={searchForms.Year}
              onChange={(e) => setSearchForms((prev) => ({ ...prev, Year: +e.target.value }))}
              required
              helperText={!searchForms.Year ? "Car Year is required" : ""}
              error={!searchForms.Year}
            />
            <TextField
              label="Car Condition"
              fullWidth
              margin="normal"
              value={searchForms.Condition}
              onChange={(e) => setSearchForms((prev) => ({ ...prev, Condition: +e.target.value }))}
              required
              helperText={!searchForms.Condition ? "Car Condition is required" : ""}
              error={!searchForms.Condition}
            />
            <Button
              fullWidth
              type="submit"
              variant="contained"
              startIcon={<Search />}
              disabled={isLoading || !searchForms.Year || !searchForms.Condition}
            >
              Search
            </Button>
      </Box>
          </CustomTabPanel>

<CustomTabPanel value={value} index={3}>
    <Button
      fullWidth
      type="button"
      variant="contained"
      startIcon={<Search />}
      onClick={handleSubmit}
    >
      Show All Cars
    </Button>

</CustomTabPanel>

          <CustomTabPanel value={value} index={4}>
            <Box component="form" onSubmit={handleSubmit}>
            <TextField
              label="VIN"
              fullWidth
              margin="normal"
              value={searchForms.vin}
              onChange={(e) => setSearchForms((prev) => ({ ...prev, vin: e.target.value }))}
              required
              helperText={!searchForms.vin ? "VIN is required" : ""}
              error={!searchForms.vin}
            />

            <Button
              fullWidth
              type="submit"
              variant="contained"
              startIcon={<Search />}
              disabled={isLoading || !searchForms.vin.trim() }
            >
              Search
            </Button>
            </Box>
          </CustomTabPanel>


          <CustomTabPanel value={value} index={5}>
            <Box component="form" onSubmit={handleSubmit}>
            <TextField
              label="VIN"
              fullWidth
              margin="normal"
              value={searchForms.vin}
              onChange={(e) => setSearchForms((prev) => ({ ...prev, vin: e.target.value }))}
              required
              helperText={!searchForms.vin ? "VIN is required" : ""}
              error={!searchForms.vin}
            />

            <Button
              fullWidth
              type="submit"
              variant="contained"
              startIcon={<Search />}
              disabled={isLoading || !searchForms.vin.trim() }
            >
              Search
            </Button>
            </Box>
          </CustomTabPanel>
          <div>
            {xmlContent && <pre>{xmlContent}</pre>}
          </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  );
});

XmlViewerDialog.displayName = 'XmlViewerDialog';

export default XmlViewerDialog;
