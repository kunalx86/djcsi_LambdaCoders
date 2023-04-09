/* eslint-disable react/prop-types */
// Soft UI Dashboard React components
import SoftBox from "components/SoftBox";
import SoftTypography from "components/SoftTypography";
import SoftAvatar from "components/SoftAvatar";
import SoftBadge from "components/SoftBadge";
import Child from "./Child";
// Images
import team2 from "assets/images/team-2.jpg";
import team3 from "assets/images/team-3.jpg";
import team4 from "assets/images/team-4.jpg";


export function Author({ image, name, age }) {
  return (
    <SoftBox display="flex" alignItems="center" px={1} py={0.5}>
      <SoftBox mr={2}>
        <SoftAvatar src={image} alt={name} size="sm" variant="rounded" />
      </SoftBox>
      <SoftBox display="flex" flexDirection="column">
        <SoftTypography variant="button" fontWeight="medium">
          {name}
        </SoftTypography>
        <SoftTypography variant="caption" color="secondary">
          {age}
        </SoftTypography>
      </SoftBox>
    </SoftBox>
  );
}

export function Function({ job, org }) {
  return (
    <SoftBox display="flex" flexDirection="column">
      <SoftTypography variant="caption" fontWeight="medium" color="text">
        {job}
      </SoftTypography>

    </SoftBox>
  );
}


export const authorsTableData = {

  // columns: [
  //   { name: "Name", align: "left" },
  //   { name: "Website", align: "left" },
  //   { name: "Block", align: "center" },
  //   { name: "Suggested", align: "center" },
  //   { name: "action", align: "center" },
  // ],
  // rows: [
  //   childs.map((child, i) => (
  //     child.visits.map((visit, j) => (
  //       {
  //         name: <Author image={team2} name={child.firstName} age={child.age} />,
  //         website: <Function job={visit.url} />,
  //         Block: (
  //           visit.isblocked ? (
  //             <SoftBadge variant="gradient" badgeContent="online" color="success" size="xs" container />
  //           ) : (
  //             <SoftBadge variant="gradient" badgeContent="online" color="error" size="xs" container />
  //           )
  //         ),
  //         suggested: (
  //           <SoftTypography variant="caption" color="secondary" fontWeight="medium">
  //             {visit.suggestBlocked}
  //           </SoftTypography>
  //         ),
  //       }
  //     ))
  //   ))
  // ]

};

export default authorsTableData;
