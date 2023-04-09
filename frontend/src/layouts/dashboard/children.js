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
import { updateChildren } from "api/parent";
import { getChildren } from "api/parent";


// Soft UI Dashboard React examples
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import SoftButton from "components/SoftButton";
import Tooltip from "@mui/material/Tooltip";
// Soft UI Dashboard React base styles
import typography from "assets/theme/base/typography";

// Dashboard layout components
import { useParams } from "react-router-dom";

// Data
import reportsBarChartData from "layouts/dashboard/data/reportsBarChartData";
import gradientLineChartData from "layouts/dashboard/data/gradientLineChartData";
import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useState } from "react";
import { getChildrens } from "api/parent";
import { Modal, Box, Typography } from "@mui/material";
import SoftInput from "components/SoftInput";
import Card from "@mui/material/Card";


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

function Children() {
    const filters = ["abusive", "offensive", "adult", "misleading"]
    const { size } = typography;
    const { chart, items } = reportsBarChartData;
    const navigate = useNavigate();
    const [user, setUser] = useState(JSON.parse(localStorage.getItem("profile"))?.user)
    const [childrens, setChildrens] = useState([]);
    const [loading, setLoading] = useState(false);
    const [childId, setChildId] = useState(useParams().childId);
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
            await getChildren(childId).then((res) => {
                console.log(res.data)
                setFormData({ ...res.data });
                let temp = [];
                let j = 0;
                for (let i = 0; i < 4; i++) {
                    if (res.data.contentFiltering[j] == filters[i]) {
                        temp.push(true);
                        j++;
                    } else {
                        temp.push(false);
                    }
                }
                let tempData = res.data;
                tempData.contentFiltering = temp;
                setFormData({ ...tempData });
            })
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
        await updateChildren(childId, formData).then((res) => {
            window.location.reload();
        }).catch(error => {
            console.log(error)
        })


    }
    return (
        <DashboardLayout>
            <DashboardNavbar />
            <Card >
                <SoftBox p={2}>
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
                                        {formData?.blockedWebsites?.map((web, i) => (
                                            <>
                                                <SoftInput type="text" placeholder="Web Url" name="website" ml={3} value={web} onChange={(e) => { handleWebChange(i, e.target.value) }} />
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
                            &nbsp;
                            <SoftBox style={{ "display": "flex" }}>
                                <SoftTypography component="label" variant="body2" fontWeight="bold" mt={2} ml={6} >
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
                                                <Checkbox checked={formData?.contentFiltering[0]} name="abusive" />
                                            }
                                            label="abusive"
                                            onChange={e => handleCheckBox(e, 0)}
                                        />
                                        <FormControlLabel
                                            control={
                                                <Checkbox checked={formData?.contentFiltering[1]} name="offensive" />
                                            }
                                            label="offensive"
                                            onChange={e => handleCheckBox(e, 1)}

                                        />
                                        <FormControlLabel
                                            control={
                                                <Checkbox checked={formData?.contentFiltering[2]} name="adult" />
                                            }
                                            label="adult"
                                            onChange={e => handleCheckBox(e, 2)}

                                        />
                                        <FormControlLabel
                                            control={
                                                <Checkbox checked={formData?.contentFiltering[3]} name="misleading" />
                                            }
                                            label="misleading"
                                            onChange={e => handleCheckBox(e, 3)}

                                        />
                                    </FormGroup>


                                </FormControl>
                            </SoftBox>
                            <SoftBox>
                                <SoftTypography ml={6}>
                                    Token : {childId}
                                </SoftTypography>
                            </SoftBox>

                            <SoftBox style={{ "display": "flex" }} ml={10} mt={5}>
                                <SoftBox py={5} align="center">
                                    <SoftButton variant="gradient" color="dark" onClick={(e) => { handleSubmit(e) }}>
                                        {loading ? "...Loading" : "Save"}
                                    </SoftButton>
                                </SoftBox>
                                <SoftBox py={5} align="center" ml={10}>
                                    <SoftButton variant="gradient" onClick={() => { navigate("/") }} disabled={loading}>
                                        Cancel
                                    </SoftButton>
                                </SoftBox>
                            </SoftBox>
                        </SoftBox>
                    </Typography>
                </SoftBox>
            </Card>
        </DashboardLayout>
    );
}

export default Children;
