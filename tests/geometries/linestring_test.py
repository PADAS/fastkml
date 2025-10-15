# Copyright (C) 2023  Christian Ledermann
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

"""Test the geometry classes."""

import pygeoif.geometry as geo
import pytest

from fastkml import exceptions
from fastkml.enums import Verbosity
from fastkml.exceptions import GeometryError
from fastkml.exceptions import KMLParseError
from fastkml.geometry import Coordinates
from fastkml.geometry import LineString
from tests.base import Lxml
from tests.base import StdLibrary


class TestLineString(StdLibrary):
    def test_init(self) -> None:
        """Test the init method."""
        ls = geo.LineString(((1, 2), (2, 0)))

        line_string = LineString(geometry=ls)

        assert line_string.geometry == ls
        assert line_string.altitude_mode is None
        assert line_string.extrude is None

    def test_unequal_coordinates(self) -> None:
        coords = Coordinates()
        lines = LineString()

        assert lines != coords

    def test_geometry_error(self) -> None:
        """Test GeometryError."""
        p = geo.LineString(((1, 2), (2, 0)))
        q = Coordinates(ns="ns")

        with pytest.raises(GeometryError):
            LineString(geometry=p, kml_coordinates=q)

    def test_to_string(self) -> None:
        """Test the to_string method."""
        ls = geo.LineString(((1, 2), (2, 0)))

        line_string = LineString(geometry=ls)

        assert "LineString" in line_string.to_string()
        assert (
            "coordinates>1.000000,2.000000 2.000000,0.000000</"
            in line_string.to_string(precision=6)
        )

    def test_from_string(self) -> None:
        """Test the from_string method."""
        linestring = LineString.from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "<coordinates>"
            "-122.364383,37.824664,0 -122.364152,37.824322,0"
            "</coordinates>"
            "</LineString>",
        )

        assert linestring.geometry == geo.LineString(
            ((-122.364383, 37.824664, 0), (-122.364152, 37.824322, 0)),
        )

    def test_mixed_2d_3d_coordinates_from_string(self) -> None:
        linestring = LineString.from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "<coordinates>"
            "-122.364383,37.824664 -122.364152,37.824322,0"
            "</coordinates>"
            "</LineString>",
        )

        assert not linestring

    def test_mixed_2d_3d_coordinates_from_string_relaxed(self) -> None:
        line_string = LineString.from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "<coordinates>"
            "-122.364383,37.824664 -122.364152,37.824322,0"
            "</coordinates>"
            "</LineString>",
            strict=False,
        )

        assert not line_string

    def test_empty_from_string(self) -> None:
        """Test the from_string method with an empty LineString."""
        linestring = LineString.from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "<coordinates>"
            "</coordinates>"
            "</LineString>",
        )

        assert not linestring.geometry

    def test_no_coordinates_from_string(self) -> None:
        """Test the from_string method with no coordinates."""
        linestring = LineString.from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>1</extrude>"
            "<tessellate>1</tessellate>"
            "</LineString>",
        )

        assert not linestring.geometry

    def test_from_string_invalid_coordinates_non_numerical(self) -> None:
        """Test the from_string method with invalid coordinates."""
        with pytest.raises(
            KMLParseError,
            match=r"^Invalid coordinates in",
        ):
            LineString.from_string(
                '<LineString xmlns="http://www.opengis.net/kml/2.2">'
                "<extrude>1</extrude>"
                "<tessellate>1</tessellate>"
                "<coordinates>"
                "foo,bar"
                "</coordinates>"
                "</LineString>",
            )

    def test_from_string_invalid_coordinates_nan(self) -> None:
        line_string = LineString.from_string(
            '<LineString xmlns="http://www.opengis.net/kml/2.2">'
            "<extrude>false</extrude>"
            "<tessellate>true</tessellate>"
            "<coordinates>"
            "-70.64950,-35.31494,2178 -70.64898,-35.31520,2121 "
            "-70.65240,-35.32666,1930 -70.65347,-35.32906,NaN "
            "-70.65340,-35.33055,1640  -70.64347,-35.34734,1468"
            "</coordinates>"
            "</LineString>",
        )

        assert line_string.geometry
        assert len(line_string.geometry.coords) == 5
        assert line_string.to_string()

    def test_from_string_invalid_extrude(self) -> None:
        """Test the from_string method."""
        with pytest.raises(
            exceptions.KMLParseError,
        ):
            LineString.from_string(
                '<LineString id="my-id" targetId="target_id" '
                'xmlns="http://www.opengis.net/kml/2.2">'
                "<extrude>invalid</extrude>"
                "</LineString>",
            )

    def test_from_string_invalid_tessellate(self) -> None:
        """Test the from_string method."""
        with pytest.raises(
            exceptions.KMLParseError,
        ):
            LineString.from_string(
                '<LineString id="my-id" targetId="target_id" '
                'xmlns="http://www.opengis.net/kml/2.2">'
                "<tessellate>invalid</tessellate>"
                "</LineString>",
            )

    def test_to_string_terse_default(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))
        line_string = LineString(geometry=ls, extrude=False, tessellate=False)

        xml = line_string.to_string(verbosity=Verbosity.terse)

        assert "tessellate" not in xml
        assert "extrude" not in xml

    def test_to_string_terse(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))
        line_string = LineString(geometry=ls, extrude=True, tessellate=True)

        xml = line_string.to_string(verbosity=Verbosity.terse)

        assert "tessellate>1</" in xml
        assert "extrude>1</" in xml

    def test_to_string_verbose_default(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))
        line_string = LineString(geometry=ls, extrude=False, tessellate=False)

        xml = line_string.to_string(verbosity=Verbosity.verbose)

        assert "tessellate>0</" in xml
        assert "extrude>0</" in xml

    def test_to_string_verbose(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))
        line_string = LineString(geometry=ls, extrude=True, tessellate=True)

        xml = line_string.to_string(verbosity=Verbosity.verbose)

        assert "tessellate>1</" in xml
        assert "extrude>1</" in xml

    def test_to_string_verbose_none(self) -> None:
        ls = geo.LineString(((1, 2), (2, 0)))
        line_string = LineString(geometry=ls)

        xml = line_string.to_string(verbosity=Verbosity.verbose)

        assert "tessellate>0</" in xml
        assert "extrude>0</" in xml

    def test_garmin_single_coordinate_linestring(self) -> None:
        """Test that single-coordinate LineStrings are handled gracefully (Garmin fix)."""
        # Create a LineString with only one coordinate (like Garmin devices sometimes produce)
        coords = Coordinates(coords=[(0.0, 0.0)])  # Only one coordinate
        linestring = LineString(kml_coordinates=coords)

        # This should return None and log a warning
        geometry = linestring.geometry

        assert geometry is None, "Single-coordinate LineString should return None"

    def test_garmin_single_coordinate_linestring_with_warning(self, caplog) -> None:
        """Test that single-coordinate LineStrings log a warning."""
        import logging
        
        # Set up logging to capture warnings
        logger = logging.getLogger('fastkml.geometry')
        logger.setLevel(logging.WARNING)
        
        # Create a LineString with only one coordinate
        coords = Coordinates(coords=[(0.0, 0.0)])
        linestring = LineString(kml_coordinates=coords)

        # This should log a warning
        with caplog.at_level(logging.WARNING):
            geometry = linestring.geometry

        assert geometry is None
        assert "LineStrings must have at least 2 coordinate tuples" in caplog.text

    def test_garmin_single_coordinate_linestring_from_string(self) -> None:
        """Test that single-coordinate LineStrings from XML are handled gracefully."""
        # Create XML with only one coordinate
        xml = '''<LineString xmlns="http://www.opengis.net/kml/2.2">
            <coordinates>0.0,0.0</coordinates>
        </LineString>'''
        
        linestring = LineString.from_string(xml)
        
        # This should return None due to the Garmin fix
        geometry = linestring.geometry
        assert geometry is None, "Single-coordinate LineString from XML should return None"

    def test_valid_linestring_after_garmin_fix(self) -> None:
        """Test that valid LineStrings still work after the Garmin fix."""
        # Test with valid LineString (2+ coordinates)
        coords_valid = Coordinates(coords=[(0.0, 0.0), (1.0, 1.0)])  # Two coordinates
        linestring_valid = LineString(kml_coordinates=coords_valid)

        geometry_valid = linestring_valid.geometry

        assert geometry_valid is not None, "Valid LineString should not return None"
        assert len(geometry_valid.coords) == 2, "Valid LineString should have 2 coordinates"

    def test_garmin_single_coordinate_linestring_with_altitude(self) -> None:
        """Test that single-coordinate LineStrings with altitude are handled gracefully."""
        # Create a LineString with only one coordinate including altitude
        coords = Coordinates(coords=[(0.0, 0.0, 100.0)])  # One coordinate with altitude
        linestring = LineString(kml_coordinates=coords)

        geometry = linestring.geometry

        assert geometry is None, "Single-coordinate LineString with altitude should return None"

    def test_garmin_empty_coordinates(self) -> None:
        """Test that empty coordinates are handled gracefully."""
        # Create a LineString with empty coordinates
        coords = Coordinates(coords=[])
        linestring = LineString(kml_coordinates=coords)

        geometry = linestring.geometry

        assert geometry is None, "Empty coordinates should return None"

    def test_garmin_none_coordinates(self) -> None:
        """Test that None coordinates are handled gracefully."""
        # Create a LineString with None coordinates
        linestring = LineString(kml_coordinates=None)

        geometry = linestring.geometry

        assert geometry is None, "None coordinates should return None"

    def test_garmin_fix_preserves_existing_behavior(self) -> None:
        """Test that the Garmin fix doesn't break existing LineString behavior."""
        # Test with a valid 3D LineString
        coords_3d = Coordinates(coords=[(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0)])
        linestring_3d = LineString(kml_coordinates=coords_3d)
        
        geometry_3d = linestring_3d.geometry
        assert geometry_3d is not None
        assert len(geometry_3d.coords) == 3
        
        # Test with a valid 2D LineString
        coords_2d = Coordinates(coords=[(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)])
        linestring_2d = LineString(kml_coordinates=coords_2d)
        
        geometry_2d = linestring_2d.geometry
        assert geometry_2d is not None
        assert len(geometry_2d.coords) == 3


class TestLineStringLxml(Lxml, TestLineString):
    """Test with lxml."""
