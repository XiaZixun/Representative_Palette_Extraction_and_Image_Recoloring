#include "data.h"
#include "utility.h"
#include <QFile>
#include <QDebug>
#include <algorithm>
#include <cmath>
#include <QProgressDialog>
#include <QThread>
#include <QMessagebox>
#include <QTime>
#include <omp.h>
#include <map>
#include "my_util.h"
#include <fstream>

using namespace std;

#define M_PI 3.14159265358979323846
#define ESP 1e-6


Data::Data()
{

}

void Data::OpenImage(QString fileName)
{
	QImage image(fileName);
	image_height = image.height();
	image_width = image.width();
	image_depth = 3;

	long long totalSize = image_width * image_height * image_depth;
	if (recolored_image != nullptr)
	{
		delete[] recolored_image;
		recolored_image = nullptr;
	}
	if (original_image != nullptr)
	{
		delete[] original_image;
		original_image = nullptr;
	}

	recolored_image = new double[totalSize];
	original_image = new double[totalSize];

	for (int i = 0; i < image_height; i++) {
		QRgb * line = (QRgb *)image.scanLine(i);
		for (int j = 0; j < image_width; j++) {
			original_image[i*image_width*image_depth + j * image_depth + 0] = qRed(line[j]) / 255.0;
			original_image[i*image_width*image_depth + j * image_depth + 1] = qGreen(line[j]) / 255.0;
			original_image[i*image_width*image_depth + j * image_depth + 2] = qBlue(line[j]) / 255.0;
		}

	}

	memcpy(recolored_image, original_image, sizeof(double)*totalSize);


	emit updated();
}

void Data::OpenPalette(string fileName)
{
	ifstream in(fileName);
	double v1, v2, v3, v4;
	char c;

	vector<vec3> rgb_ch_vertices;
	vector<int3> rgb_ch_faces;
	vector<vector<int>> rgb_ch_tetras;
	while (!in.eof()) {
		in >> c;
		if (c == 'v') {
			in >> v1 >> v2 >> v3;
			vec3 vert(v1, v2, v3);
			rgb_ch_vertices.push_back(vert);
		}
		else if (c == 'f') {
			in >> v1 >> v2 >> v3;
			int3 face(v1 - 1, v2 - 1, v3 - 1);
			rgb_ch_faces.push_back(face);
		}
		else if(c=='t') {
			in>> v1 >> v2 >> v3 >> v4;
			vector<int> tetra={(int)v1-1,(int)v2-1,(int)v3-1,(int)v4-1};
			rgb_ch_tetras.push_back(tetra);
		}
		else
			break;

		c = 'x';
	}

	changed_palette.vertices = rgb_ch_vertices;
	changed_palette.faces = rgb_ch_faces;
	tetras=rgb_ch_tetras;

	original_palette = changed_palette;

	in.close();
	emit updated();
}

void Data::reset()
{
	mvc_weights.clear();
	mvc_weights.resize(image_width*image_height);
	is_mvc_calculated = false;
}

inline double angle(const myfloat3 & u1, const myfloat3 & u2) {
	float u_norm = (u1 - u2).norm();
	return 2.0 * asin(u_norm / 2.0);
}

void Data::setPaletteColor(int id, QColor c) {
	double r = qRed(c.rgb()) / 255.0;
	double g = qGreen(c.rgb()) / 255.0;
	double b = qBlue(c.rgb()) / 255.0;
	changed_palette.vertices[id] = vec3(r, g, b);
}

inline float Volume(vec3 const &a,vec3 const &b,vec3 const &c,vec3 const &d) {
	vec3 u=b-a,v=c-a,w=d-a;
	return abs(dot(cross(v,w),u)/6);
}

vector<float> Data::ComputeSingleVertexMVCWeights(int vid, const vec3 &o) {

	float const eps=1e-7;
	vector<vec3> &vertices = original_palette.vertices;
	int vcnt = vertices.size();
	vector<float> weight={};
	float min_dist=2;

	for(auto const &tetra:tetras) {
		vec3 const v0=vertices[tetra[0]],v1=vertices[tetra[1]],
			v2=vertices[tetra[2]],v3=vertices[tetra[3]];
		float vol=Volume(v0,v1,v2,v3),vol0=Volume(o,v1,v2,v3),
			vol1=Volume(v0,o,v2,v3),vol2=Volume(v0,v1,o,v3),vol3=Volume(v0,v1,v2,o);
		if(abs((vol0+vol1+vol2+vol3)-vol)<eps&&abs((vol0+vol1+vol2+vol3)-vol)/vol<min_dist&&vol>eps) {
			min_dist=abs((vol0+vol1+vol2+vol3)-vol)/vol;
			weight=vector<float>(vcnt,0);
			vol=vol0+vol1+vol2+vol3;
			weight[tetra[0]]=vol0/vol;
			weight[tetra[1]]=vol1/vol;
			weight[tetra[2]]=vol2/vol;
			weight[tetra[3]]=vol3/vol;
		}
	}
	return weight;
}

const void Data::ComputeMVCWeights() {

//#pragma omp parallel for num_threads(32)

	for (int i = 0; i < image_width * image_height * image_depth; i += image_depth) {
		vec3 x(
			original_image[i + 0],
			original_image[i + 1],
			original_image[i + 2]
		);
		int vid = i / image_depth;
		vector<float> weights = ComputeSingleVertexMVCWeights(vid, x);
		if(weights.empty())
			weights = ComputeSingleVertexMVCWeightsForceInside(vid, x);

		mvc_weights[vid] = weights;
	}

	is_mvc_calculated = true;
	ExportLayers("./delaunay_layers");
	QMessageBox::information(NULL, "Info", "MVC finished", QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes);
	
}

vec3 Data::RecolorSinglePixel(int vid, const vec3 &x) {
	vec3 ans(0.f, 0.f, 0.f);

	for (int i = 0; i < mvc_weights[vid].size(); i++) {

		float w = mvc_weights[vid][i];
		vec3 v;
		if(is_mvc_calculated)
			v = changed_palette.vertices[i];
		else
			v = original_palette.vertices[i];
		ans = ans + v * w;
	}
	return ans;
}

void Data::Recolor() {
	if (!is_mvc_calculated)
		return;

	QTime time1;
	time1.start();

#pragma omp parallel for num_threads(32)
	for (int i = 0; i < image_width * image_height * image_depth; i += image_depth)
	{
		int frame_pix_offset = image_width * image_height * image_depth;
		vec3 x(
			original_image[i + 0],
			original_image[i + 1],
			original_image[i + 2]
		);

		vec3 y = RecolorSinglePixel(i / image_depth, x);

		recolored_image[i + 0] = y[0];
		recolored_image[i + 1] = y[1];
		recolored_image[i + 2] = y[2];
	}

	qDebug() << "Recolor time: " << time1.elapsed() / 1000.0 << "s";
	emit updated();
}

void Data::ExportOriginalVideo(string path) {
	if (!is_mvc_calculated)
		return;

	QTime time;
	time.start();

	int k = 0;

	QSize size(image_height, image_width);
	QImage image(size, QImage::Format_ARGB32);

#pragma omp parallel for num_threads(32)
	for (int i = 0; i < image_width * image_height * image_depth; i += image_depth)
	{
		vec3 x(
			original_image[i + 0],
			original_image[i + 1],
			original_image[i + 2]
		);


		int row = i / (image_height * image_depth);
		int col = (i - row*image_height * image_depth) / image_depth;
		image.setPixel(col, row, qRgb(x[0] * 255, x[1] * 255, x[2] * 255));

	}
	image.save((path + "/original.png").c_str(), "PNG", 100);
}

void Data::ExportRecoloredImage(string path) {


	uchar *data = new uchar[image_width * image_height * image_depth];

	#pragma omp parallel for num_threads(32)
	for (int i = 0; i < image_width * image_height * image_depth; i++)
	{
		int x = static_cast<int>(recolored_image[i] * 255);
		if (x > 255) x = 255;
		if (x < 0) x = 0;

		data[i] = static_cast<uchar>(x);
	}

	cout << endl;
	//for (int i = 0; i < 3; i++)
		//cout << (int)data[i * 3] << "," << (int)data[i * 3 + 1] << "," << (int)data[i * 3 + 2] << endl;

	QImage image(data, image_width, image_height, image_width * 3, QImage::Format_RGB888);
	image.save((path + "/recolored.png").c_str(), "PNG", 100);
	delete[] data;
}


//Yili Wang's code
vector<float> Data::ComputeSingleVertexMVCWeightsForceInside(int vid, const vec3 &x) {

	float min_distance = FLT_MAX;
	vec3 close_point;

	for (int i = 0; i < original_palette.faces.size(); i++)
	{
		int3 triangle = original_palette.faces[i];
		vec3 triangle_vertices[3];

		triangle_vertices[0] = original_palette.vertices[triangle.x];
		triangle_vertices[1] = original_palette.vertices[triangle.y];
		triangle_vertices[2] = original_palette.vertices[triangle.z];
		vec3 my_close_point = closesPointOnTriangle(triangle_vertices, x);
		float my_dis = (x - my_close_point).sqrnorm();

		if (my_dis < min_distance) {
			min_distance = my_dis;
			close_point = my_close_point;
		}
	}

	vec3 projection(close_point[0], close_point[1], close_point[2]);
	return ComputeSingleVertexMVCWeights(vid, projection);
}

vec3 Data::VertexForeceInside(int const vid,vec3 const &x) {
	float min_distance = FLT_MAX;
	vec3 close_point;

	for (int i = 0; i < original_palette.faces.size(); i++)
	{
		int3 triangle = original_palette.faces[i];
		vec3 triangle_vertices[3];

		triangle_vertices[0] = original_palette.vertices[triangle.x];
		triangle_vertices[1] = original_palette.vertices[triangle.y];
		triangle_vertices[2] = original_palette.vertices[triangle.z];
		vec3 my_close_point = closesPointOnTriangle(triangle_vertices, x);
		float my_dis = (x - my_close_point).sqrnorm();

		if (my_dis < min_distance) {
			min_distance = my_dis;
			close_point = my_close_point;
		}
	}

	return close_point;
}

void Data::resetPaletteColor(int id) {
	changed_palette.vertices[id] = original_palette.vertices[id];
	Recolor();
	emit updated();
}

void Data::resetAllPaletteColors() {
	for (int i = 0; i < changed_palette.vertices.size(); i++)
		changed_palette.vertices[i] = original_palette.vertices[i];
}

void Data::ImportChangedPalette(string path) {
	ifstream ifs(path);
	int n; ifs >> n;
	for (int i = 0; i < n; i++) {
		ifs >> changed_palette.vertices[i][0] >> changed_palette.vertices[i][1]
			>> changed_palette.vertices[i][2];
	}
	emit updated();
}


void Data::ExportChangedPalette(string path) {
	ofstream ofs(path);
	ofs << changed_palette.vertices.size() << endl;
	for (int i = 0; i < changed_palette.vertices.size(); i++) {

		ofs << changed_palette.vertices[i][0] << " " <<
			changed_palette.vertices[i][1] << " " <<
			changed_palette.vertices[i][2] << " " << endl;
	}
}

vector<int3> Data::GetFaces() const {
	vector<int3> faces={};
	vector<vector<int>> choosers={{0,1,2},{0,1,3},{0,2,3},{1,2,3}};
	for(auto const &t:tetras)
		for(auto const &c:choosers) {
			vector<int> f={t[c[0]],t[c[1]],t[c[2]]};
			std::sort(f.begin(),f.end());
			faces.push_back(int3(f[0],f[1],f[2]));
		}
	std::sort(faces.begin(),faces.end(),[](int3 const &a,int3 const &b)->bool {
		if(a.x!=b.x)
			return a.x<b.x;
		if(a.y!=b.y)
			return a.y<b.y;
		return a.z<b.z;
		});
	faces.erase(std::unique(faces.begin(),faces.end(),[](int3 const &a,int3 const &b)->bool {
		return a.x==b.x&&a.y==b.y&&a.z==b.z;
		}),faces.end());
	return faces;
}

void Data::ExportLayers(string const &path) {
	if(!is_mvc_calculated)
		return;
	for(int k=0;k<original_palette.vertices.size();++k)
		ExportLayer(k,path);
}

void Data::ExportLayer(int const k,string const &path) {
	vec3 vertex=original_palette.vertices[k];
	uchar *data = new uchar[image_width * image_height * image_depth];
	vec3 black(0.0,0.0,0.0),white(0.5,0.5,0.5);
	int rect_len=40;

	for(int i=0;i<image_width*image_height*image_depth;i+=image_depth) {
		int idx=i/image_depth;
		int row=idx/image_width,col=idx%image_width;
		vec3 bgcolor=(row/rect_len)%2==(col/rect_len)%2?white:black;
		vec3 pixel_color=vertex*mvc_weights[idx][k]+(1-mvc_weights[idx][k])*bgcolor;
		for(int j=0;j<3;++j) {
			int x=static_cast<int>(pixel_color[j] * 255);
			if(x>255)
				x=255;
			if(x<0)
				x=0;
			data[i+j]=static_cast<uchar>(x);
		}
	}
	QImage image(data, image_width, image_height, image_width * 3, QImage::Format_RGB888);
	image.save((path + "/layer_"+to_string(k)+".png").c_str(), "PNG", 100);
	delete[] data;
}