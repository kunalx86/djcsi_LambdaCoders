/**
=========================================================
* Soft UI Dashboard React - v4.0.0
=========================================================

* Product Page: https://www.creative-tim.com/product/soft-ui-dashboard-react
* Copyright 2022 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

// @mui material components
import Grid from "@mui/material/Grid";
import Icon from "@mui/material/Icon";
import { IconButton } from "@mui/material";
// Soft UI Dashboard React components
import SoftBox from "components/SoftBox";
import SoftTypography from "components/SoftTypography";
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import FormGroup from '@mui/material/FormGroup';
import Checkbox from '@mui/material/Checkbox';
import { addChildren } from "api/parent";


// Soft UI Dashboard React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import SoftButton from "components/SoftButton";
import Tooltip from "@mui/material/Tooltip";
// Soft UI Dashboard React base styles
import typography from "assets/theme/base/typography";

// Dashboard layout components
import BuildByDevelopers from "layouts/dashboard/components/BuildByDevelopers";
import WorkWithTheRockets from "layouts/dashboard/components/WorkWithTheRockets";
import Projects from "layouts/dashboard/components/Projects";
import OrderOverview from "layouts/dashboard/components/OrderOverview";

// Data
import reportsBarChartData from "layouts/dashboard/data/reportsBarChartData";
import gradientLineChartData from "layouts/dashboard/data/gradientLineChartData";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useState } from "react";
import { getChildrens } from "api/parent";
import { Modal, Box, Typography } from "@mui/material";
import SoftInput from "components/SoftInput";
import { LocalHospitalTwoTone } from "@mui/icons-material";

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 800,
  bgcolor: 'background.paper',
  boxShadow: 60,
  borderRadius: '25px',
  p: 4,

};

function Dashboard() {
  const filters = ["abusive", "offensive", "adult", "misleading"]
  const { size } = typography;
  const { chart, items } = reportsBarChartData;
  const navigate = useNavigate();
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("profile"))?.user)
  const [childrens, setChildrens] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    age: 0,
    blockedWebsites: [""],
    hours: 0,
    minutes: 0,
    gender: "",
    contentFiltering: [false, false, false, false]
  })

  useEffect(() => {
    setUser(JSON.parse(localStorage.getItem("profile"))?.user)
    if (!user) {
      navigate("/signIn")
    }


    async function fetchData() {
      const response = await getChildrens(user._id);
      setChildrens(response.data)
    }
    fetchData();


  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  const handleCheckBox = (e, i) => {
    formData.contentFiltering[i] = e.target.checked;
    setFormData({ ...formData })
  }


  const handleClose = (i) => {

    if (formData.blockedWebsites.length > 1) {
      formData.blockedWebsites.splice(i, 1);
    }
    setFormData({ ...formData })
  }

  const handleWebChange = (i, text) => {
    formData.blockedWebsites[i] = text;
    setFormData({ ...formData })

  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    let temp = [];
    for (let i = 0; i < 4; i++) {
      if (formData.contentFiltering[i] == true) {
        temp.push(filters[i]);
      }
    }
    formData.contentFiltering = temp;
    setFormData({ ...formData });
    await addChildren(formData).then((res) => {
      setOpen(false);
      let data = JSON.parse(localStorage.getItem("profile"))
      data.user = res.data;
      localStorage.setItem("profile", JSON.stringify(data));
      window.location.reload();
    }).catch(error => {
      console.log(error)
    })


  }
  return (
    <DashboardLayout>
      <DashboardNavbar />
      <SoftBox py={3}>
        <SoftBox mb={3}>
          <Grid container spacing={3}>
            {childrens?.map((child, i) => (
              <>
                <Grid item xs={12} lg={6}>
                  <BuildByDevelopers i={i + 1} id={child._id} firstName={child.firstName} lastName={child.lastName} age={child.age} gender={child.gender} />
                </Grid>
              </>
            ))}
          </Grid>
          <SoftBox py={5} align="center">
            <SoftButton variant="gradient" color="dark" onClick={() => { setOpen(true) }}>
              <Icon sx={{ fontWeight: "bold" }}>add</Icon>
              &nbsp;Add New Children
            </SoftButton>
          </SoftBox>

        </SoftBox>
      </SoftBox>
      <Modal
        open={open}
        onClose={() => { setOpen(false) }}
        aria-labelledby="modal-modal-title"
        aria-describedby="modal-modal-description"
      >

        <Box sx={style}>
          <Typography id="modal-modal-title" variant="h4" component="h2">
            Add Children
          </Typography>
          <Typography id="modal-modal-description" md={{ mt: 5 }} mt={3}>
            <SoftBox component="form" role="form" >
              <Grid container style={{ "display": "flex" }}>
                <SoftBox mb={2} ml={5}>
                  <SoftBox mb={1} ml={0.5}>
                    <SoftTypography component="label" variant="body2" fontWeight="bold">
                      First Name
                    </SoftTypography>
                  </SoftBox>
                  <SoftInput type="text" placeholder="First Name" name="firstName" value={formData.firstName} onChange={handleChange} />
                </SoftBox>
                <SoftBox mb={2} ml={5}>
                  <SoftBox mb={1} ml={0.5}>
                    <SoftTypography component="label" variant="body2" fontWeight="bold">
                      Last Name
                    </SoftTypography>
                  </SoftBox>
                  <SoftInput type="text" placeholder="Last Name" name="lastName" value={formData.lastName} onChange={handleChange} />
                </SoftBox>
                <SoftBox mb={2} ml={5}>
                  <SoftBox mb={1} ml={0.5}>
                    <SoftTypography component="label" variant="body2" fontWeight="bold">
                      Age
                    </SoftTypography>
                  </SoftBox>
                  <SoftInput type="number" placeholder="0" name="age" value={formData.age} onChange={handleChange} />
                </SoftBox>
              </Grid>

              <SoftBox style={{ "display": "flex" }}>

                <SoftBox mb={2} ml={5} >
                  <SoftBox mb={1} ml={0.5}>
                    <SoftTypography component="label" variant="body2" fontWeight="bold">
                      Website to Block
                    </SoftTypography>
                  </SoftBox>
                  <SoftBox style={{ "display": "flex" }} >
                    {formData.blockedWebsites.map((web, i) => (
                      <>
                        <SoftInput type="text" placeholder="Web Url" name="website" ml={3} onChange={(e) => { handleWebChange(i, e.target.value) }} />
                        <Icon sx={{ cursor: "pointer" }} fontSize="small" mt={3} onClick={(e) => { handleClose(i) }}>
                          close
                        </Icon>
                        &nbsp;&nbsp;&nbsp;
                      </>
                    ))}
                  </SoftBox>
                </SoftBox>
              </SoftBox>
              <IconButton size="small" ml={5}
                onClick={() => {
                  formData.blockedWebsites.push("");
                  setFormData({ ...formData });
                  console.log(formData)

                }}
              >
                <Icon
                  sm={({ palette: { dark, white } }) => ({
                    color: light ? white.main : dark.main,
                  })}
                  // fontSize="2rem"
                  style={{ "marginLeft": "25px" }}
                >
                  add
                </Icon>
                <SoftTypography
                  variant="button"
                  fontWeight="small"
                  style={{ "marginLeft": "5px" }}

                >
                  Add
                </SoftTypography>
              </IconButton>
              <Grid container style={{ "display": "flex", "marginTop": "15px" }}>
                <SoftBox mb={2} ml={5}>
                  <SoftBox mb={1} ml={0.5}>
                    <SoftTypography component="label" variant="body2" fontWeight="bold">
                      Hours
                    </SoftTypography>
                  </SoftBox>
                  <SoftInput type="number" placeholder="0" name="hours" value={formData.hours} onChange={handleChange} />
                </SoftBox>
                <SoftBox mb={2} ml={5}>
                  <SoftBox mb={1} ml={0.5}>
                    <SoftTypography component="label" variant="body2" fontWeight="bold">
                      Minutes
                    </SoftTypography>
                  </SoftBox>
                  <SoftInput type="number" placeholder="0" name="minutes" value={formData.minutes} onChange={handleChange} />
                </SoftBox>
              </Grid>
              <SoftBox style={{ "display": "flex" }}>
                <SoftTypography component="label" variant="body2" fontWeight="bold" mt={2} ml={5} >
                  Gender
                </SoftTypography>
                <FormControl style={{ "marginTop": "45px" }}>
                  <RadioGroup
                    row
                    aria-labelledby="demo-row-radio-buttons-group-label"
                    name="gender"
                    value={formData.gender}
                    onChange={handleChange}


                  >
                    <FormControlLabel value="female" control={<Radio />} label="Female" />
                    &nbsp;&nbsp;&nbsp;
                    <FormControlLabel value="male" control={<Radio />} label="Male" />
                  </RadioGroup>
                </FormControl>

                <SoftTypography component="label" variant="body2" fontWeight="bold" mt={2} ml={15} >
                  Content Filtering
                </SoftTypography>
                <FormControl
                  required
                  component="fieldset"
                  sx={{ m: 3 }}
                  variant="standard"
                  style={{ "marginTop": "10px" }}
                >
                  <FormGroup>
                    <FormControlLabel
                      control={
                        <Checkbox checked={formData.contentFiltering[0]} name="abusive" />
                      }
                      label="abusive"
                      onChange={e => handleCheckBox(e, 0)}
                    />
                    <FormControlLabel
                      control={
                        <Checkbox checked={formData.contentFiltering[1]} name="offensive" />
                      }
                      label="offensive"
                      onChange={e => handleCheckBox(e, 1)}

                    />
                    <FormControlLabel
                      control={
                        <Checkbox checked={formData.contentFiltering[2]} name="adult" />
                      }
                      label="adult"
                      onChange={e => handleCheckBox(e, 2)}

                    />
                    <FormControlLabel
                      control={
                        <Checkbox checked={formData.contentFiltering[3]} name="misleading" />
                      }
                      label="misleading"
                      onChange={e => handleCheckBox(e, 3)}

                    />
                  </FormGroup>


                </FormControl>
              </SoftBox>

              <SoftBox style={{ "display": "flex" }} ml={10} mt={5}>
                <SoftBox py={5} align="center">
                  <SoftButton variant="gradient" color="dark" onClick={(e) => { handleSubmit(e) }}>
                    {loading ? "...Loading" : "Save"}
                  </SoftButton>
                </SoftBox>
                <SoftBox py={5} align="center" ml={10}>
                  <SoftButton variant="gradient" onClick={() => { setOpen(false) }} disabled={loading}>
                    Cancel
                  </SoftButton>
                </SoftBox>
              </SoftBox>
            </SoftBox>
          </Typography>
        </Box>

      </Modal>
    </DashboardLayout>
  );
}

export default Dashboard;
