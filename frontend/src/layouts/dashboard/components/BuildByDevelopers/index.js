
// @mui material components
import Card from "@mui/material/Card";
import Grid from "@mui/material/Grid";
import Icon from "@mui/material/Icon";
import PropTypes from "prop-types";

// Soft UI Dashboard React components
import SoftBox from "components/SoftBox";
import SoftTypography from "components/SoftTypography";

// Images
import wavesWhite from "assets/images/shapes/waves-white.svg";
import rocketWhite from "assets/images/illustrations/rocket-white.png";
import girl from "assets/images/girl.jpg";
import boy from "assets/images/boy.jpg";
import { useNavigate } from "react-router-dom";


function BuildByDevelopers({ i, firstName, lastName, gender, age, id }) {
  const navigate = useNavigate();
  const handleClick = () => {
    navigate(`/dashboard/children/${id}`)
  }
  return (
    <Card>
      <SoftBox p={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} lg={6}>
            <SoftBox display="flex" flexDirection="column" height="100%">
              <SoftBox pt={1} mb={0.5}>
                <SoftTypography variant="body2" color="text" fontWeight="medium">
                  Children {i}
                </SoftTypography>
              </SoftBox>
              <SoftTypography variant="h5" fontWeight="bold" gutterBottom>
                {firstName} {lastName}
              </SoftTypography>
              <SoftBox mb={6}>
                <SoftTypography variant="body1" color="text">
                  {age}
                </SoftTypography>
                <SoftTypography variant="body1" color="text">
                  {gender}
                </SoftTypography>
                <SoftTypography variant="body2" color="text">
                  Token : ***********
                </SoftTypography>
              </SoftBox>
              <SoftTypography
                component="a"
                href="#"
                variant="button"
                color="text"
                fontWeight="medium"
                sx={{
                  mt: "auto",
                  mr: "auto",
                  display: "inline-flex",
                  alignItems: "center",
                  cursor: "pointer",

                  "& .material-icons-round": {
                    fontSize: "1.125rem",
                    transform: `translate(2px, -0.5px)`,
                    transition: "transform 0.2s cubic-bezier(0.34,1.61,0.7,1.3)",
                  },

                  "&:hover .material-icons-round, &:focus  .material-icons-round": {
                    transform: `translate(6px, -0.5px)`,
                  },
                }}
                onClick={handleClick}
              >
                Show More
                <Icon sx={{ fontWeight: "bold" }}>arrow_forward</Icon>
              </SoftTypography>
            </SoftBox>
          </Grid>
          <Grid item xs={12} lg={5} sx={{ position: "relative", ml: "auto" }}>
            <SoftBox
              height="100%"
              display="grid"
              justifyContent="center"
              alignItems="center"
              bgColor="info"
              borderRadius="lg"
              variant="gradient"
            >
              <SoftBox
                component="img"
                src={wavesWhite}
                alt="waves"
                display="block"
                position="absolute"
                left={0}
                width="100%"
                height="100%"
              />
              {gender === "male" ? (

                <SoftBox component="img" src={boy} alt="rocket" width="100%" pt={3} />
              ) : (
                <SoftBox component="img" src={girl} alt="rocket" width="100%" pt={3} />

              )}
            </SoftBox>
          </Grid>
        </Grid>
      </SoftBox>
    </Card>
  );
}


BuildByDevelopers.propTypes = {
  i: PropTypes.number,
  firstName: PropTypes.string,
  lastName: PropTypes.string,
  age: PropTypes.number,
  gender: PropTypes.string,
  id: PropTypes.string
}

export default BuildByDevelopers;
